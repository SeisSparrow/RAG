#!/usr/bin/env python3
"""
Simplified Audio Processor - Fallback version without ffmpeg dependency
This version handles large files by using a different approach
"""

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

class SimpleAudioProcessor:
    def __init__(self):
        self.client = OpenAI()
        
    def transcribe_audio_simple(self, audio_path: str) -> Dict[str, Any]:
        """
        Simple transcription approach - try to transcribe the full file
        If it fails due to size, provide helpful error message
        """
        try:
            print(f"Attempting to transcribe: {audio_path}")
            print("Note: If the file is too large (>25MB), this will fail.")
            print("Consider using a shorter audio file or splitting it manually.")
            
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
        except Exception as e:
            if "413" in str(e) or "Maximum content size limit" in str(e):
                print("❌ File too large for OpenAI Whisper API (25MB limit)")
                print("📋 Solutions:")
                print("1. Use a shorter audio file")
                print("2. Install ffmpeg and use the full audio_processor.py")
                print("3. Manually split the audio file into smaller chunks")
                print("4. Use an online tool to compress the audio")
                return None
            else:
                logging.error(f"Error transcribing audio: {e}")
                logging.error(traceback.format_exc())
                return None
    
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
        transcription = self.transcribe_audio_simple(audio_path)
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
    audio_processor = SimpleAudioProcessor()
    audio_path = "audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3"
    
    # Process the audio file
    chunks = audio_processor.process_audio_file(audio_path, 'audio_index', chunk_duration=60)
    
    if chunks:
        print(f"\nProcessed {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"\nChunk {i+1}:")
            print(f"Time: {chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s")
            print(f"Text: {chunk['text'][:200]}...")
