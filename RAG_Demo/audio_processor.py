import os
import json
import time
import logging
import traceback
from typing import List, Dict, Any
from openai import OpenAI
from config import get_es
from embedding import local_embedding
import tiktoken
import subprocess
import tempfile

class AudioProcessor:
    def __init__(self):
        self.client = OpenAI()
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for OpenAI Whisper
        
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    def split_audio_file(self, audio_path: str, chunk_duration: int = 600) -> List[str]:
        """
        Split large audio file into smaller chunks using ffmpeg
        Returns list of temporary chunk file paths
        """
        file_size = self.get_file_size(audio_path)
        if file_size <= self.max_file_size:
            return [audio_path]  # File is small enough, no need to split
        
        print(f"File size ({file_size / (1024*1024):.1f}MB) exceeds limit. Splitting into chunks...")
        
        # Create temporary directory for chunks
        temp_dir = tempfile.mkdtemp()
        chunk_files = []
        
        try:
            # Get audio duration using ffprobe
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
            
            # Calculate number of chunks needed
            num_chunks = int(total_duration / chunk_duration) + 1
            
            print(f"Splitting {total_duration:.1f}s audio into {num_chunks} chunks of {chunk_duration}s each...")
            
            # Split audio using ffmpeg
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_file = os.path.join(temp_dir, f"chunk_{i:03d}.mp3")
                
                split_cmd = [
                    'ffmpeg', '-i', audio_path, '-ss', str(start_time),
                    '-t', str(chunk_duration), '-c', 'copy', '-y', chunk_file
                ]
                
                result = subprocess.run(split_cmd, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(chunk_file):
                    chunk_files.append(chunk_file)
                    print(f"Created chunk {i+1}/{num_chunks}: {chunk_file}")
                else:
                    print(f"Failed to create chunk {i+1}: {result.stderr}")
            
            return chunk_files
            
        except Exception as e:
            print(f"Error splitting audio file: {e}")
            # Clean up temporary files
            for chunk_file in chunk_files:
                try:
                    os.remove(chunk_file)
                except:
                    pass
            return [audio_path]  # Fallback to original file
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API
        Handles large files by splitting them into chunks
        Returns transcription with timestamps and metadata
        """
        try:
            # Check if file needs to be split
            chunk_files = self.split_audio_file(audio_path)
            
            if len(chunk_files) == 1 and chunk_files[0] == audio_path:
                # File is small enough, transcribe directly
                return self._transcribe_single_file(audio_path)
            else:
                # File was split, transcribe each chunk and combine
                return self._transcribe_multiple_chunks(chunk_files, audio_path)
                
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            logging.error(traceback.format_exc())
            return None
    
    def _transcribe_single_file(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe a single audio file"""
        with open(audio_path, 'rb') as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return {
            "text": transcript.text,
            "language": transcript.language,
            "duration": transcript.duration,
            "segments": transcript.segments if hasattr(transcript, 'segments') else []
        }
    
    def _transcribe_multiple_chunks(self, chunk_files: List[str], original_path: str) -> Dict[str, Any]:
        """Transcribe multiple audio chunks and combine results"""
        all_text = []
        all_segments = []
        total_duration = 0
        language = None
        
        print(f"Transcribing {len(chunk_files)} audio chunks...")
        
        for i, chunk_file in enumerate(chunk_files):
            print(f"Transcribing chunk {i+1}/{len(chunk_files)}...")
            
            try:
                with open(chunk_file, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                
                # Adjust timestamps for each chunk
                chunk_offset = i * 600  # 10 minutes per chunk
                
                if hasattr(transcript, 'segments') and transcript.segments:
                    for segment in transcript.segments:
                        # Adjust timestamps to account for chunk offset
                        segment.start += chunk_offset
                        segment.end += chunk_offset
                        all_segments.append({
                            'start': segment.start,
                            'end': segment.end,
                            'text': segment.text
                        })
                
                all_text.append(transcript.text)
                total_duration += transcript.duration if hasattr(transcript, 'duration') else 0
                
                if language is None:
                    language = transcript.language
                    
            except Exception as e:
                print(f"Error transcribing chunk {i+1}: {e}")
                continue
            finally:
                # Clean up temporary chunk file
                try:
                    os.remove(chunk_file)
                except:
                    pass
        
        # Clean up temporary directory
        try:
            temp_dir = os.path.dirname(chunk_files[0])
            os.rmdir(temp_dir)
        except:
            pass
        
        return {
            "text": " ".join(all_text),
            "language": language,
            "duration": total_duration,
            "segments": all_segments
        }
    
    def create_audio_chunks(self, transcription: Dict[str, Any], chunk_duration: int = 60) -> List[Dict[str, Any]]:
        """
        Split audio transcription into time-based chunks for better retrieval
        """
        chunks = []
        segments = transcription.get('segments', [])
        
        if not segments:
            # If no segments, create a single chunk
            chunks.append({
                "text": transcription['text'],
                "start_time": 0,
                "end_time": transcription.get('duration', 0),
                "chunk_id": 0
            })
            return chunks
        
        current_chunk_start = 0
        current_chunk_text = ""
        current_chunk_segments = []
        chunk_id = 0
        
        for segment in segments:
            segment_start = segment.get('start', 0)
            segment_end = segment.get('end', 0)
            segment_text = segment.get('text', '').strip()
            
            # If adding this segment would exceed chunk duration, save current chunk
            if segment_end - current_chunk_start > chunk_duration and current_chunk_text:
                chunks.append({
                    "text": current_chunk_text.strip(),
                    "start_time": current_chunk_start,
                    "end_time": current_chunk_segments[-1].get('end', 0) if current_chunk_segments else 0,
                    "chunk_id": chunk_id,
                    "segments": current_chunk_segments.copy()
                })
                
                # Start new chunk
                current_chunk_start = segment_start
                current_chunk_text = segment_text
                current_chunk_segments = [segment]
                chunk_id += 1
            else:
                current_chunk_text += " " + segment_text
                current_chunk_segments.append(segment)
        
        # Add the last chunk
        if current_chunk_text:
            chunks.append({
                "text": current_chunk_text.strip(),
                "start_time": current_chunk_start,
                "end_time": current_chunk_segments[-1].get('end', 0) if current_chunk_segments else 0,
                "chunk_id": chunk_id,
                "segments": current_chunk_segments
            })
        
        return chunks
    
    def process_audio_file(self, audio_path: str, es_index: str, chunk_duration: int = 60):
        """
        Process audio file: transcribe, chunk, and store in Elasticsearch
        """
        print(f"Processing audio file: {audio_path}")
        
        # Step 1: Transcribe audio
        print("Transcribing audio...")
        transcription = self.transcribe_audio(audio_path)
        if not transcription:
            print("Failed to transcribe audio")
            return
        
        print(f"Transcription completed. Duration: {transcription.get('duration', 0):.2f} seconds")
        print(f"Language: {transcription.get('language', 'unknown')}")
        
        # Step 2: Create chunks
        print("Creating audio chunks...")
        chunks = self.create_audio_chunks(transcription, chunk_duration)
        print(f"Created {len(chunks)} chunks")
        
        # Step 3: Process chunks and store in Elasticsearch
        es = get_es()
        batch = []
        
        for i, chunk in enumerate(chunks):
            batch.append(chunk)
            
            # Process in batches of 25
            if len(batch) == 25 or i == len(chunks) - 1:
                try:
                    # Generate embeddings for batch
                    embeddings = local_embedding([chunk['text'] for chunk in batch])
                    
                    for j, chunk in enumerate(batch):
                        # Create metadata
                        metadata = {
                            "file_type": "audio",
                            "file_name": os.path.basename(audio_path),
                            "start_time": chunk['start_time'],
                            "end_time": chunk['end_time'],
                            "chunk_id": chunk['chunk_id'],
                            "duration": chunk['end_time'] - chunk['start_time'],
                            "language": transcription.get('language', 'unknown')
                        }
                        
                        body = {
                            'text': chunk['text'],
                            'vector': embeddings[j],
                            'metadata': metadata,
                            'file_id': hash(audio_path),  # Simple file ID
                            'image_id': None  # Not applicable for audio
                        }
                        
                        # Store in Elasticsearch
                        retry = 0
                        while retry <= 5:
                            try:
                                es.index(index=es_index, body=body)
                                break
                            except Exception as e:
                                print(f'[Elastic Error] {str(e)} retry')
                                retry += 1
                                time.sleep(1)
                    
                    batch = []
                    print(f"Processed batch {i//25 + 1}")
                    
                except Exception as e:
                    print(f"Error processing batch: {e}")
                    batch = []
        
        print(f"Successfully processed and stored {len(chunks)} audio chunks")
        return chunks

def num_tokens_from_string(string):   
    encoding = tiktoken.get_encoding('cl100k_base')
    num_tokens = len(encoding.encode(string))
    return num_tokens

if __name__ == '__main__':
    # Example usage
    audio_processor = AudioProcessor()
    audio_path = "audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3"
    
    # Process the audio file
    chunks = audio_processor.process_audio_file(audio_path, 'audio_index', chunk_duration=60)
    
    if chunks:
        print(f"\nProcessed {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"\nChunk {i+1}:")
            print(f"Time: {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s")
            print(f"Text: {chunk['text'][:200]}...")
