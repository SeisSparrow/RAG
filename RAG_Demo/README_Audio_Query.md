# 🎵 Audio Query System - RAG Framework

This guide shows you how to use the RAG (Retrieval Augmented Generation) framework to query audio content, specifically using the example file `audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3`.

## 🎯 Overview

The Audio Query System allows you to:
- Transcribe audio files using OpenAI Whisper
- Handle large audio files by automatic splitting
- Create time-based chunks for precise queries
- Query audio content using natural language
- Get summaries with exact time references
- Analyze speech patterns and statistics

## 🏗️ System Architecture

```
Audio File → Speech-to-Text → Time-based Chunking → Embeddings → Vector Database → Query Processing → Response
```

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Navigate to the project directory
cd /Users/zhennan/Documents/GithubRepos/RAG/RAG_Demo

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Required Services
- **Elasticsearch**: Running on `localhost:9200`
- **OpenAI API**: For speech transcription and LLM responses
- **ffmpeg**: For handling large audio files (automatically installed)

### 3. API Key Setup
```bash
# Set your OpenAI API key
export OPENAI_API_KEY='your-actual-api-key-here'

# Or create a .env file
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env
```

## 🚀 Quick Start

### Step 1: Setup and Validation
```bash
# Check all prerequisites
python3 setup_audio_rag.py
```

### Step 2: Run Complete Demo
```bash
# Process audio and run interactive queries
python3 audio_rag_demo.py
```

### Step 3: Manual Processing
```bash
# Process audio file manually
python3 audio_processor.py
```

## 📖 Detailed Usage

### 1. Audio Processing

The `audio_processor.py` module handles audio transcription and processing:

```python
from audio_processor import AudioProcessor

# Initialize processor
processor = AudioProcessor()

# Process audio file
chunks = processor.process_audio_file(
    audio_path="audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3",
    es_index='audio_index',
    chunk_duration=60  # 60-second chunks
)
```

**What happens during processing:**
- **Large File Handling**: Automatically splits files >25MB using ffmpeg
- **Speech-to-Text**: Uses OpenAI Whisper for accurate transcription
- **Time-based Chunking**: Creates segments with precise timestamps
- **Embedding Generation**: Creates vector representations for semantic search
- **Storage**: Stores in Elasticsearch with time metadata

### 2. Audio Querying

The `audio_queries.py` module provides specialized querying capabilities:

```python
from audio_queries import AudioQueryProcessor

# Initialize query processor
processor = AudioQueryProcessor()

# Get summary of specific time range
summary = processor.get_audio_summary(
    query="What is discussed in the first 5 minutes?",
    es_index='audio_index',
    time_range=(0, 5)  # First 5 minutes
)

# Search for specific content
results = processor.search_audio_content(
    query="peace",
    es_index='audio_index',
    time_range=(2, 10)  # Between 2-10 minutes
)

# Get audio statistics
stats = processor.count_sentences_in_audio('audio_index')

# Analyze speech patterns
patterns = processor.analyze_speech_patterns('audio_index')
```

### 3. Advanced Query Types

#### Time-based Queries
```python
# Summary of specific time ranges
summary_5min = processor.get_audio_summary(
    "What is discussed in the first 5 minutes?",
    'audio_index',
    time_range=(0, 5)
)

summary_2to5 = processor.get_audio_summary(
    "Summarize content from 2-5 minutes",
    'audio_index',
    time_range=(2, 5)
)
```

#### Content Search with Time References
```python
# Search with time filtering
peace_results = processor.search_audio_content(
    "peace",
    'audio_index',
    time_range=(0, 10)  # Only search first 10 minutes
)

# Results include precise time information
for result in peace_results:
    print(f"Time: {result['start_time_minutes']:.1f}-{result['end_time_minutes']:.1f} min")
    print(f"Text: {result['text']}")
```

#### Statistical Analysis
```python
# Get comprehensive audio statistics
stats = processor.count_sentences_in_audio('audio_index')
print(f"Total sentences: {stats['total_sentences']}")
print(f"Total words: {stats['total_words']}")
print(f"Duration: {stats['total_duration_minutes']:.1f} minutes")
print(f"Words per minute: {stats['average_words_per_minute']:.1f}")

# Analyze speech patterns
patterns = processor.analyze_speech_patterns('audio_index')
print(f"Speech pacing: {patterns['speech_pacing']}")
print(f"Sentences per minute: {patterns['sentences_per_minute']:.1f}")
```

## 🔍 Example Queries

Here are example queries you can try with the Kennedy speech:

### Content Analysis Queries
```python
queries = [
    "What is the main topic of this speech?",
    "What does Kennedy say about peace?",
    "What are the key themes discussed?",
    "What is the overall message?",
    "What does the speaker say about nuclear weapons?"
]
```

### Time-based Queries
```python
queries = [
    "What is discussed in the first 5 minutes?",
    "Summarize the content from 2 to 5 minutes",
    "What happens in the last 3 minutes?",
    "What is said between 5-10 minutes?",
    "What are the main points in the first half?"
]
```

### Statistical Queries
```python
queries = [
    "How many sentences are in the speech?",
    "What's the speaking pace?",
    "How long is the entire speech?",
    "How many times is 'peace' mentioned?",
    "What's the average sentence length?"
]
```

### Specific Content Search
```python
queries = [
    "Find mentions of the Soviet Union",
    "What does Kennedy say about democracy?",
    "Search for quotes about freedom",
    "What are the key quotes in this speech?",
    "Find references to nuclear weapons"
]
```

## 📊 Query Results Format

Each query returns results with the following structure:

```python
{
    'text': 'transcribed text content',
    'start_time_minutes': 2.5,
    'end_time_minutes': 3.2,
    'start_time_seconds': 150.0,
    'end_time_seconds': 192.0,
    'score': 0.95,
    'file_name': 'President John F. Kennedy\'s Peace Speech - C-SPAN.mp3'
}
```

## 🛠️ Configuration

### Audio Processing Parameters
In `audio_processor.py`, you can adjust:

```python
# Chunk duration for transcription
chunk_duration = 60  # seconds per chunk

# File size limit for OpenAI Whisper
max_file_size = 25 * 1024 * 1024  # 25MB

# Chunk duration for retrieval
retrieval_chunk_duration = 60  # seconds per retrieval chunk
```

### Query Parameters
In `audio_queries.py`:

```python
# Number of results to return
top_k = 10

# Time range filtering
time_range = (start_minutes, end_minutes)

# Reranking parameters
rerank_top_k = 5
```

## 🎯 Best Practices

### 1. Query Formulation
- Be specific about time ranges when needed
- Use natural language for content queries
- Ask focused questions for better results
- Use comparative language for analysis

### 2. Time-based Queries
- Specify exact time ranges for precise results
- Use minutes for easier understanding
- Consider speech pacing when setting ranges
- Use relative time references ("first 5 minutes")

### 3. Content Analysis
- Use summary queries for overview
- Use search queries for specific content
- Combine multiple queries for comprehensive analysis
- Check time references for context

## 🔧 Troubleshooting

### Common Issues

1. **Large File Error (413)**
   ```bash
   # The system now automatically handles this with ffmpeg
   # No manual intervention needed
   ```

2. **OpenAI API Error**
   ```bash
   # Check API key
   echo $OPENAI_API_KEY
   
   # Test API connection
   python3 -c "from openai import OpenAI; client = OpenAI(); print('API working')"
   ```

3. **ffmpeg Not Found**
   ```bash
   # Install ffmpeg (already done)
   brew install ffmpeg
   
   # Verify installation
   python3 check_ffmpeg.py
   ```

4. **Elasticsearch Connection Error**
   ```bash
   # Check Elasticsearch status
   curl -X GET "localhost:9200/"
   
   # Update config.py if needed
   ```

### Performance Optimization

1. **Faster Processing**
   - Use shorter chunk durations for faster transcription
   - Process in parallel (modify code for concurrent processing)
   - Use faster embedding models

2. **Memory Management**
   - Process large files in smaller batches
   - Clear temporary files after processing
   - Monitor Elasticsearch memory usage

## 📈 Advanced Features

### 1. Multi-Audio Queries
```python
# Process multiple audio files into the same index
audio_files = [
    "audio/speech1.mp3",
    "audio/speech2.mp3",
    "audio/interview.mp3"
]

for audio_file in audio_files:
    processor.process_audio_file(audio_file, 'multi_audio_index')
```

### 2. Custom Time Segmentation
```python
# Custom chunking strategies
def create_custom_chunks(transcription, segment_duration=30):
    # Create 30-second chunks instead of 60-second
    return processor.create_audio_chunks(transcription, segment_duration)
```

### 3. Speech Analysis
```python
# Advanced speech pattern analysis
def analyze_emotion_patterns(es_index):
    # Custom analysis for emotional content
    # Detect pauses, emphasis, etc.
    pass

def detect_speaker_changes(es_index):
    # Identify different speakers
    # Useful for interviews or multi-speaker content
    pass
```

### 4. Real-time Processing
```python
# Process streaming audio
def process_streaming_audio(audio_stream, es_index):
    # Process audio as it's being recorded
    # Useful for live transcription and querying
    pass
```

## 🎉 Example Complete Workflow

```python
#!/usr/bin/env python3
"""
Complete Audio Query Workflow Example
"""

from audio_processor import AudioProcessor
from audio_queries import AudioQueryProcessor
from es_functions import create_elastic_index

def main():
    # 1. Setup
    index_name = 'kennedy_speech'
    audio_file = "audio/President John F. Kennedy's Peace Speech - C-SPAN.mp3"
    
    # 2. Create index
    create_elastic_index(index_name)
    
    # 3. Process audio
    processor = AudioProcessor()
    chunks = processor.process_audio_file(audio_file, index_name)
    
    # 4. Query examples
    query_processor = AudioQueryProcessor()
    
    # Time-based queries
    print("🎯 Time-based Queries")
    print("=" * 50)
    
    summary_5min = query_processor.get_audio_summary(
        "What is discussed in the first 5 minutes?",
        index_name,
        time_range=(0, 5)
    )
    print(f"First 5 minutes: {summary_5min}")
    
    # Content search
    print("\n🔍 Content Search")
    print("=" * 50)
    
    peace_results = query_processor.search_audio_content("peace", index_name)
    for i, result in enumerate(peace_results[:3]):
        print(f"{i+1}. Time: {result['start_time_minutes']:.1f}-{result['end_time_minutes']:.1f} min")
        print(f"   Text: {result['text'][:200]}...")
    
    # Statistics
    print("\n📊 Statistics")
    print("=" * 50)
    
    stats = query_processor.count_sentences_in_audio(index_name)
    print(f"Total sentences: {stats['total_sentences']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Duration: {stats['total_duration_minutes']:.1f} minutes")
    print(f"Words per minute: {stats['average_words_per_minute']:.1f}")
    
    # Speech analysis
    print("\n🗣️ Speech Analysis")
    print("=" * 50)
    
    patterns = query_processor.analyze_speech_patterns(index_name)
    print(f"Speech pacing: {patterns['speech_pacing']}")
    print(f"Sentences per minute: {patterns['sentences_per_minute']:.1f}")

if __name__ == "__main__":
    main()
```

## 🎮 Interactive Demo

Run the interactive demo for a hands-on experience:

```bash
python3 audio_rag_demo.py
```

The demo will:
1. Process your audio file automatically
2. Show example queries and results
3. Provide an interactive query interface
4. Display statistics and analysis

## 📚 Additional Resources

- **OpenAI Whisper**: Speech-to-text transcription
- **ffmpeg**: Audio file processing and splitting
- **Elasticsearch**: Vector database for audio content
- **RAG Framework**: Retrieval Augmented Generation pattern
- **Time-based Chunking**: Precise temporal segmentation

## 🤝 Contributing

To extend the audio query system:

1. Add support for more audio formats
2. Implement speaker diarization
3. Add emotion detection
4. Integrate real-time processing
5. Add custom audio analysis features
6. Implement multi-language support

## 🎵 Supported Audio Formats

- **MP3**: Primary format (recommended)
- **WAV**: High quality audio
- **M4A**: Apple audio format
- **FLAC**: Lossless audio
- **OGG**: Open source format

## ⚡ Performance Tips

1. **File Size**: Keep files under 25MB for direct processing
2. **Chunk Duration**: 60 seconds provides good balance of context and precision
3. **Batch Processing**: Process multiple files in sequence
4. **Caching**: Reuse embeddings for similar content
5. **Indexing**: Use appropriate Elasticsearch settings for audio content

---

**Ready to query your audio content with the power of RAG!** 🎵🚀
