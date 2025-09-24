# 🎵 Audio RAG System - Quick Start Guide

## ✅ What's Ready
- ✅ Python environment set up
- ✅ All dependencies installed
- ✅ Elasticsearch running
- ✅ ffmpeg installed for large file processing
- ✅ Audio file available

## 🔑 Final Step: Set OpenAI API Key

You need to set your OpenAI API key to use the transcription service. Choose one option:

### Option 1: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY='your-actual-api-key-here'
```

### Option 2: Create .env file
```bash
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env
```

## 🚀 Run the Audio RAG System

Once you set the API key, run:

```bash
# 1. Activate environment
cd /Users/zhennan/Documents/GithubRepos/RAG/RAG_Demo
source venv/bin/activate

# 2. Set API key (replace with your actual key)
export OPENAI_API_KEY='your-actual-api-key-here'

# 3. Run the complete demo
python3 audio_rag_demo.py
```

## 🎯 What You Can Query

The system will process the Kennedy speech and let you ask questions like:

### 📊 Content Analysis
- *"What is discussed in the first 5 minutes?"*
- *"Summarize the content from 2 to 5 minutes"*
- *"What is the main theme of the speech?"*

### 📈 Statistics
- *"How many sentences are in the audio?"*
- *"What's the speaking pace (words per minute)?"*
- *"How long is the entire speech?"*

### 🔍 Specific Content Search
- *"What does the speaker say about peace?"*
- *"Find mentions of freedom"*
- *"What are the key quotes about democracy?"*

### ⏱️ Time-based Queries
- *"What happens in the first 3 minutes?"*
- *"Summarize the last 2 minutes"*
- *"What is discussed between 5-10 minutes?"*

## 🔧 How It Works

1. **Audio Processing**: Uses ffmpeg to split large files into manageable chunks
2. **Transcription**: OpenAI Whisper converts speech to text with timestamps
3. **Chunking**: Splits transcript into time-based segments for better retrieval
4. **Embeddings**: Creates vector representations for semantic search
5. **Storage**: Stores in Elasticsearch for fast retrieval
6. **Querying**: Hybrid search (keyword + semantic) with reranking

## 🆘 Troubleshooting

### File Too Large Error
- ✅ **Fixed**: The system now automatically splits large files using ffmpeg

### Elasticsearch Connection Error
- ✅ **Fixed**: Updated config to work with your setup

### Missing Dependencies
- ✅ **Fixed**: All dependencies are installed

### OpenAI API Error
- 🔑 **Solution**: Set your API key as shown above

## 📁 Files Created

- `audio_processor.py` - Handles large file splitting and transcription
- `audio_queries.py` - Specialized query functions for audio content
- `audio_rag_demo.py` - Complete demo with interactive interface
- `setup_audio_rag.py` - Setup validation script

## 🎉 Ready to Go!

Just set your OpenAI API key and run the demo. The system will:
1. Split your large audio file into chunks
2. Transcribe each chunk with timestamps
3. Create embeddings and store in Elasticsearch
4. Provide an interactive query interface

You'll be able to ask natural language questions about the Kennedy speech content with precise time references!
