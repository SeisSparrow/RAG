#!/usr/bin/env python3
"""
Quick setup script for Audio RAG system
This script helps you get started with audio content analysis using RAG
"""

import os
import sys
from config import get_es
from es_functions import create_elastic_index

def check_elasticsearch_connection():
    """Check if Elasticsearch is accessible"""
    try:
        es = get_es()
        es.info()
        print("✅ Elasticsearch connection successful")
        return True
    except Exception as e:
        print(f"❌ Elasticsearch connection failed: {e}")
        print("\nPlease make sure Elasticsearch is running and accessible.")
        print("You may need to update the credentials in config.py")
        return False

def check_openai_api():
    """Check if OpenAI API is accessible"""
    try:
        from openai import OpenAI
        client = OpenAI()
        # Try a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✅ OpenAI API connection successful")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("\nPlease make sure you have:")
        print("1. Set your OpenAI API key as an environment variable: export OPENAI_API_KEY='your-key'")
        print("2. Or create a .env file with: OPENAI_API_KEY=your-key")
        return False

def check_audio_file():
    """Check if the audio file exists"""
    audio_path = "audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3"
    if os.path.exists(audio_path):
        print(f"✅ Audio file found: {audio_path}")
        return True
    else:
        print(f"❌ Audio file not found: {audio_path}")
        print("\nPlease make sure the audio file exists in the audio/ directory")
        return False

def setup_elasticsearch_index():
    """Create the Elasticsearch index for audio content"""
    try:
        index_name = "audio_index"
        create_elastic_index(index_name)
        print(f"✅ Created Elasticsearch index: {index_name}")
        return True
    except Exception as e:
        print(f"⚠️  Index creation failed (might already exist): {e}")
        return True  # Index might already exist

def main():
    """Main setup function"""
    print("🎵 Audio RAG System Setup")
    print("=" * 40)
    
    # Check all prerequisites
    checks = [
        ("Elasticsearch Connection", check_elasticsearch_connection),
        ("OpenAI API Access", check_openai_api),
        ("Audio File", check_audio_file),
        ("Elasticsearch Index", setup_elasticsearch_index)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All checks passed! You're ready to run the Audio RAG system.")
        print("\nNext steps:")
        print("1. Run: python3 audio_rag_demo.py")
        print("2. Or run individual components:")
        print("   - python3 audio_processor.py (to process audio)")
        print("   - python3 audio_queries.py (to run queries)")
    else:
        print("❌ Some checks failed. Please fix the issues above before proceeding.")
        print("\nCommon solutions:")
        print("1. For Elasticsearch: Make sure it's running on localhost:9200")
        print("2. For OpenAI API: Set your API key as an environment variable")
        print("3. For audio file: Make sure the MP3 file is in the audio/ directory")

if __name__ == "__main__":
    main()
