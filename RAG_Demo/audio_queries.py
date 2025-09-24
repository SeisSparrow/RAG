import json
from typing import Dict, Any, List
from openai import OpenAI
from retrieve_documents import elastic_search, rerank
from config import get_es

class AudioQueryProcessor:
    def __init__(self):
        self.client = OpenAI()
    
    def get_audio_summary(self, query: str, es_index: str, time_range: tuple = None) -> str:
        """
        Get summary of audio content for a specific time range or entire audio
        """
        # Modify query to focus on summary
        if time_range:
            start_time, end_time = time_range
            enhanced_query = f"Summarize the content from {start_time} to {end_time} minutes: {query}"
        else:
            enhanced_query = f"Provide a comprehensive summary of: {query}"
        
        # Search for relevant chunks
        results = elastic_search(enhanced_query, es_index)
        
        if not results:
            return "No relevant content found."
        
        # Get top results and rerank
        top_results = results[:10]
        reranked_results = rerank(enhanced_query, top_results)
        
        # Prepare context for summary generation
        context_parts = []
        for i, result in enumerate(reranked_results[:5]):
            metadata = result.get('metadata', {})
            start_time = metadata.get('start_time', 0)
            end_time = metadata.get('end_time', 0)
            
            context_parts.append(f"Time {start_time/60:.1f}-{end_time/60:.1f} minutes: {result['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Generate summary using LLM
        prompt = f"""
        Based on the following audio transcript segments, provide a comprehensive summary.
        
        Query: {query}
        
        Audio Content:
        {context}
        
        Please provide:
        1. A clear summary of the main points
        2. Key themes or topics discussed
        3. Important details or quotes
        4. Overall tone and style of the speech
        
        Summary:
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing and summarizing audio content, particularly speeches and presentations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def count_sentences_in_audio(self, es_index: str) -> Dict[str, Any]:
        """
        Count sentences, words, and other statistics in the audio
        """
        es = get_es()
        
        # Get all audio chunks
        query = {"match_all": {}}
        response = es.search(
            index=es_index,
            query=query,
            size=1000  # Adjust based on your data size
        )
        
        total_sentences = 0
        total_words = 0
        total_duration = 0
        chunks_processed = 0
        
        for hit in response['hits']['hits']:
            text = hit['_source'].get('text', '')
            metadata = hit['_source'].get('metadata', {})
            
            # Count sentences (simple heuristic)
            sentences = len([s for s in text.split('.') if s.strip()])
            words = len(text.split())
            
            total_sentences += sentences
            total_words += words
            total_duration += metadata.get('duration', 0)
            chunks_processed += 1
        
        return {
            "total_sentences": total_sentences,
            "total_words": total_words,
            "total_duration_minutes": total_duration / 60,
            "chunks_processed": chunks_processed,
            "average_sentences_per_minute": total_sentences / (total_duration / 60) if total_duration > 0 else 0,
            "average_words_per_minute": total_words / (total_duration / 60) if total_duration > 0 else 0
        }
    
    def search_audio_content(self, query: str, es_index: str, time_range: tuple = None) -> List[Dict[str, Any]]:
        """
        Search for specific content in audio with time references
        """
        # Search for relevant content
        results = elastic_search(query, es_index)
        
        if not results:
            return []
        
        # Filter by time range if specified
        if time_range:
            start_minutes, end_minutes = time_range
            start_seconds = start_minutes * 60
            end_seconds = end_minutes * 60
            
            filtered_results = []
            for result in results:
                metadata = result.get('metadata', {})
                chunk_start = metadata.get('start_time', 0)
                chunk_end = metadata.get('end_time', 0)
                
                # Check if chunk overlaps with time range
                if chunk_start < end_seconds and chunk_end > start_seconds:
                    filtered_results.append(result)
            
            results = filtered_results
        
        # Rerank results
        reranked_results = rerank(query, results)
        
        # Format results with time information
        formatted_results = []
        for result in reranked_results:
            metadata = result.get('metadata', {})
            formatted_result = {
                "text": result['text'],
                "start_time_minutes": metadata.get('start_time', 0) / 60,
                "end_time_minutes": metadata.get('end_time', 0) / 60,
                "start_time_seconds": metadata.get('start_time', 0),
                "end_time_seconds": metadata.get('end_time', 0),
                "score": result.get('score', 0),
                "file_name": metadata.get('file_name', 'Unknown')
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def analyze_speech_patterns(self, es_index: str) -> Dict[str, Any]:
        """
        Analyze speech patterns, pacing, and structure
        """
        es = get_es()
        
        # Get all chunks with timing information
        query = {"match_all": {}}
        response = es.search(
            index=es_index,
            query=query,
            size=1000
        )
        
        chunks = []
        for hit in response['hits']['hits']:
            metadata = hit['_source'].get('metadata', {})
            chunks.append({
                'text': hit['_source'].get('text', ''),
                'start_time': metadata.get('start_time', 0),
                'end_time': metadata.get('end_time', 0),
                'duration': metadata.get('duration', 0)
            })
        
        # Sort by start time
        chunks.sort(key=lambda x: x['start_time'])
        
        # Analyze patterns
        total_duration = max([chunk['end_time'] for chunk in chunks]) if chunks else 0
        total_words = sum([len(chunk['text'].split()) for chunk in chunks])
        total_sentences = sum([len([s for s in chunk['text'].split('.') if s.strip()]) for chunk in chunks])
        
        # Calculate pacing
        words_per_minute = total_words / (total_duration / 60) if total_duration > 0 else 0
        sentences_per_minute = total_sentences / (total_duration / 60) if total_duration > 0 else 0
        
        # Analyze chunk duration distribution
        chunk_durations = [chunk['duration'] for chunk in chunks]
        avg_chunk_duration = sum(chunk_durations) / len(chunk_durations) if chunk_durations else 0
        
        return {
            "total_duration_minutes": total_duration / 60,
            "total_words": total_words,
            "total_sentences": total_sentences,
            "words_per_minute": words_per_minute,
            "sentences_per_minute": sentences_per_minute,
            "average_chunk_duration_seconds": avg_chunk_duration,
            "number_of_chunks": len(chunks),
            "speech_pacing": "fast" if words_per_minute > 200 else "moderate" if words_per_minute > 150 else "slow"
        }

def demo_audio_queries():
    """
    Demonstrate various audio query capabilities
    """
    processor = AudioQueryProcessor()
    es_index = "audio_index"
    
    print("=== Audio RAG Query Demo ===\n")
    
    # 1. Get summary of first 5 minutes
    print("1. Summary of first 5 minutes:")
    summary_5min = processor.get_audio_summary(
        "What is discussed in the first 5 minutes?", 
        es_index, 
        time_range=(0, 5)
    )
    print(summary_5min)
    print("\n" + "="*60 + "\n")
    
    # 2. Get overall summary
    print("2. Overall summary of the entire speech:")
    overall_summary = processor.get_audio_summary(
        "What is the main topic and key points of this speech?", 
        es_index
    )
    print(overall_summary)
    print("\n" + "="*60 + "\n")
    
    # 3. Count sentences and statistics
    print("3. Audio statistics:")
    stats = processor.count_sentences_in_audio(es_index)
    print(json.dumps(stats, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 4. Search for specific content
    print("4. Search for content about 'peace':")
    peace_results = processor.search_audio_content("peace", es_index)
    for i, result in enumerate(peace_results[:3]):
        print(f"Result {i+1} (Time: {result['start_time_minutes']:.1f}-{result['end_time_minutes']:.1f} min):")
        print(f"Text: {result['text'][:200]}...")
        print()
    
    # 5. Analyze speech patterns
    print("5. Speech pattern analysis:")
    patterns = processor.analyze_speech_patterns(es_index)
    print(json.dumps(patterns, indent=2))

if __name__ == '__main__':
    demo_audio_queries()
