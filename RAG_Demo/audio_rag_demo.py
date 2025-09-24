#!/usr/bin/env python3
"""
Audio RAG Demo - Complete pipeline for processing and querying audio content
This script demonstrates how to use the RAG framework for audio content analysis
"""

import os
import sys
from audio_processor import AudioProcessor
from audio_queries import AudioQueryProcessor
from es_functions import create_elastic_index, delete_elastic_index

def setup_audio_rag():
    """
    Set up the complete audio RAG system
    """
    print("=== Setting up Audio RAG System ===\n")
    
    # 1. Create Elasticsearch index for audio content
    index_name = "audio_index"
    print(f"1. Creating Elasticsearch index: {index_name}")
    try:
        create_elastic_index(index_name)
        print("✅ Index created successfully")
    except Exception as e:
        print(f"⚠️  Index creation failed (might already exist): {e}")
    
    return index_name

def process_audio_file(audio_path: str, index_name: str):
    """
    Process audio file and store in vector database
    """
    print(f"\n=== Processing Audio File: {audio_path} ===\n")
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    # Initialize audio processor
    processor = AudioProcessor()
    
    # Process the audio file
    try:
        chunks = processor.process_audio_file(audio_path, index_name, chunk_duration=60)
        if chunks:
            print(f"✅ Successfully processed {len(chunks)} audio chunks")
            return True
        else:
            print("❌ Failed to process audio file")
            return False
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        return False

def run_audio_queries(index_name: str):
    """
    Run various audio queries to demonstrate capabilities
    """
    print(f"\n=== Running Audio Queries ===\n")
    
    processor = AudioQueryProcessor()
    
    # Query 1: Summary of first 5 minutes
    print("🎯 Query 1: Summary of first 5 minutes")
    print("-" * 50)
    try:
        summary_5min = processor.get_audio_summary(
            "What is discussed in the first 5 minutes?", 
            index_name, 
            time_range=(0, 5)
        )
        print(summary_5min)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Query 2: Overall summary
    print("🎯 Query 2: Overall summary of the entire speech")
    print("-" * 50)
    try:
        overall_summary = processor.get_audio_summary(
            "What is the main topic and key points of this speech?", 
            index_name
        )
        print(overall_summary)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Query 3: Count sentences and statistics
    print("🎯 Query 3: Audio statistics and sentence count")
    print("-" * 50)
    try:
        stats = processor.count_sentences_in_audio(index_name)
        print(f"📊 Audio Statistics:")
        print(f"   • Total sentences: {stats['total_sentences']}")
        print(f"   • Total words: {stats['total_words']}")
        print(f"   • Total duration: {stats['total_duration_minutes']:.1f} minutes")
        print(f"   • Average sentences per minute: {stats['average_sentences_per_minute']:.1f}")
        print(f"   • Average words per minute: {stats['average_words_per_minute']:.1f}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Query 4: Search for specific content
    print("🎯 Query 4: Search for content about 'peace'")
    print("-" * 50)
    try:
        peace_results = processor.search_audio_content("peace", index_name)
        print(f"Found {len(peace_results)} relevant segments:")
        for i, result in enumerate(peace_results[:3]):
            print(f"\n📍 Result {i+1} (Time: {result['start_time_minutes']:.1f}-{result['end_time_minutes']:.1f} min):")
            print(f"   Text: {result['text'][:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Query 5: Analyze speech patterns
    print("🎯 Query 5: Speech pattern analysis")
    print("-" * 50)
    try:
        patterns = processor.analyze_speech_patterns(index_name)
        print(f"🗣️  Speech Analysis:")
        print(f"   • Total duration: {patterns['total_duration_minutes']:.1f} minutes")
        print(f"   • Words per minute: {patterns['words_per_minute']:.1f}")
        print(f"   • Sentences per minute: {patterns['sentences_per_minute']:.1f}")
        print(f"   • Speech pacing: {patterns['speech_pacing']}")
        print(f"   • Number of chunks: {patterns['number_of_chunks']}")
    except Exception as e:
        print(f"Error: {e}")

def interactive_queries(index_name: str):
    """
    Interactive query interface
    """
    print(f"\n=== Interactive Audio Query Interface ===\n")
    print("Enter your queries about the audio content. Type 'quit' to exit.")
    print("Example queries:")
    print("  - 'What does the speaker say about peace?'")
    print("  - 'Summarize the content from 2 to 5 minutes'")
    print("  - 'How many times is the word freedom mentioned?'")
    print("  - 'What is the main theme of the speech?'")
    print()
    
    processor = AudioQueryProcessor()
    
    while True:
        try:
            query = input("🎤 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔍 Searching for: {query}")
            print("-" * 50)
            
            # Try different query types
            if "summary" in query.lower() or "summarize" in query.lower():
                # Summary query
                result = processor.get_audio_summary(query, index_name)
                print(result)
            else:
                # Search query
                results = processor.search_audio_content(query, index_name)
                if results:
                    print(f"Found {len(results)} relevant segments:")
                    for i, result in enumerate(results[:5]):  # Show top 5
                        print(f"\n📍 Segment {i+1} (Time: {result['start_time_minutes']:.1f}-{result['end_time_minutes']:.1f} min):")
                        print(f"   {result['text'][:300]}...")
                else:
                    print("No relevant content found.")
            
            print("\n" + "="*80 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error processing query: {e}")

def main():
    """
    Main function to run the complete audio RAG demo
    """
    print("🎵 Audio RAG System Demo")
    print("=" * 50)
    
    # Audio file path
    audio_path = "audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3"
    
    # Check if audio file exists
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        print("Please make sure the audio file exists in the correct location.")
        return
    
    try:
        # Step 1: Setup
        index_name = setup_audio_rag()
        
        # Step 2: Process audio file
        success = process_audio_file(audio_path, index_name)
        if not success:
            print("❌ Failed to process audio file. Exiting.")
            return
        
        # Step 3: Run demo queries
        run_audio_queries(index_name)
        
        # Step 4: Interactive mode
        print("\n" + "="*80)
        response = input("Would you like to enter interactive query mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_queries(index_name)
        
        print("\n✅ Audio RAG demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
