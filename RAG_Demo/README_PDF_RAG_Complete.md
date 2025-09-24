# 📄 PDF RAG Demo - Complete Guide

This guide provides comprehensive documentation for the PDF RAG demo system, including both full-featured and simplified versions.

## 🎯 Overview

The PDF RAG Demo provides multiple interfaces for querying PDF documents:

1. **`pdf_rag_demo.py`** - Full-featured demo with text, images, and tables (requires OpenAI API)
2. **`pdf_rag_demo_simple.py`** - Simplified version with text and tables only (no API required)
3. **`pdf_query.py`** - Simple command-line interface for full version
4. **`pdf_query_simple.py`** - Simple command-line interface for simplified version

## 🚀 Quick Start

### Option 1: Simplified Version (Recommended for Testing)

```bash
# Simple command-line interface
python3 pdf_query_simple.py <pdf_file> <query>

# Examples
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What data is in the tables?"

# Interactive demo
python3 pdf_rag_demo_simple.py
```

### Option 2: Full-Featured Version (Requires OpenAI API)

```bash
# Simple command-line interface
python3 pdf_query.py <pdf_file> <query>

# Examples
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are shown?"

# Interactive demo
python3 pdf_rag_demo.py
```

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Navigate to the project directory
cd /Users/zhennan/Documents/GithubRepos/RAG/RAG_Demo

# Activate virtual environment
source venv/bin/activate

# Ensure all dependencies are installed
pip install -r requirements.txt
```

### 2. Required Services
- **Elasticsearch**: Running on `localhost:9200`
- **Embedding Service**: Configured in `config.py`
- **OpenAI API** (for full version only): Set `OPENAI_API_KEY` environment variable

### 3. API Key Setup (Full Version Only)
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 🔧 Usage Examples

### Text Queries (Both Versions)

```bash
# Query about document content
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What are the key principles?"
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What procedures are discussed?"
```

### Table Queries (Both Versions)

```bash
# Query about tables (use keywords like 'table', 'data', 'chart')
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What tables are in the document?"
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What data is shown in tables?"
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What statistics are presented?"
```

### Image Queries (Full Version Only)

```bash
# Query about images (use keywords like 'image', 'picture', 'figure')
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are in the document?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What do the pictures show?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What figures are displayed?"
```

### Multi-Modal Queries (Full Version Only)

```bash
# Query about relationships (use keywords like 'relationship', 'together', 'both')
python3 pdf_query.py test_pdf/image_extraction_example.pdf "How do images and text relate?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "How do tables and text work together?"
```

## 🎮 Interactive Demo Features

### Simplified Version (`pdf_rag_demo_simple.py`)
- **Text processing**: Automatic extraction and chunking
- **Table processing**: Structure detection and natural language descriptions
- **Example queries**: Pre-defined queries for each content type
- **Interactive mode**: Custom query interface
- **Processing summary**: Statistics and results overview

### Full Version (`pdf_rag_demo.py`)
- **All simplified features** plus:
- **Image processing**: Visual analysis with context augmentation
- **Multi-modal queries**: Cross-content analysis
- **Advanced features**: Relationship analysis between content types

## 📊 Query Types and Keywords

### Text Queries (Default)
- General questions about document content
- No specific keywords needed
- Examples: "What is the main topic?", "What are the key points?"

### Table Queries
**Keywords**: `table`, `chart`, `data`, `statistics`, `numbers`
- Examples: "What tables are present?", "What data is shown?"

### Image Queries (Full Version Only)
**Keywords**: `image`, `picture`, `photo`, `figure`, `diagram`
- Examples: "What images are shown?", "What do the pictures depict?"

### Multi-Modal Queries (Full Version Only)
**Keywords**: `relationship`, `relate`, `together`, `combine`, `both`
- Examples: "How do images and text relate?", "What's the relationship between tables and text?"

## 🔍 Advanced Usage

### Custom Processing Options

```python
# Simplified version - process only text (skip tables)
demo.process_pdf_file(pdf_path, process_tables=False)

# Full version - customize processing
demo.process_pdf_file(pdf_path, process_images=False, process_tables=True)
```

### Batch Processing

```python
# Process multiple files
pdf_files = [
    'test_pdf/xingshisusongfa.pdf',
    'test_pdf/table_extraction_example.pdf'
]

for pdf_file in pdf_files:
    demo.process_pdf_file(pdf_file)
```

### Direct Class Usage

```python
# Use the demo class directly
demo = SimplePDFRAGDemo()  # or PDFRAGDemo() for full version
demo.setup_pdf_rag()
demo.process_pdf_file('your_file.pdf')

# Query specific content types
text_results = demo.query_text_content("Your text query")
table_results = demo.query_table_content("Your table query")
```

## 📁 File Structure

```
RAG_Demo/
├── pdf_rag_demo.py              # Full-featured interactive demo
├── pdf_rag_demo_simple.py       # Simplified interactive demo
├── pdf_query.py                 # Simple CLI for full version
├── pdf_query_simple.py          # Simple CLI for simplified version
├── document_process.py          # Text processing
├── image_table.py               # Image and table processing
├── retrieve_documents.py        # Query and retrieval
├── es_functions.py              # Elasticsearch operations
├── config.py                    # Configuration
└── test_pdf/                    # Example PDF files
    ├── xingshisusongfa.pdf      # Chinese legal document
    ├── image_extraction_example.pdf
    └── table_extraction_example.pdf
```

## 🎯 Example Workflows

### Workflow 1: Legal Document Analysis
```bash
# Process and query legal document
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What are the key principles?"
python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "What procedures are described?"
```

### Workflow 2: Data-Rich Document Analysis
```bash
# Process and query table-rich document
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What tables are present?"
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What data is shown?"
python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf "What statistics are presented?"
```

### Workflow 3: Multi-Modal Document Analysis (Full Version)
```bash
# Process and query image-rich document
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are shown?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What do the figures illustrate?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "How do images support the text?"
```

## 🔧 Troubleshooting

### Common Issues

1. **File Not Found**
   ```bash
   # Check if file exists
   ls -la test_pdf/
   
   # Use absolute path if needed
   python3 pdf_query_simple.py /full/path/to/your/file.pdf "Your query"
   ```

2. **Elasticsearch Connection Error**
   ```bash
   # Check Elasticsearch status
   curl -X GET "localhost:9200/"
   
   # Update config.py if needed
   ```

3. **OpenAI API Error (Full Version)**
   ```bash
   # Check API key
   echo $OPENAI_API_KEY
   
   # Set API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Processing Errors**
   ```bash
   # Check file permissions
   ls -la your_file.pdf
   
   # Try with a different PDF file
   python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf "Test query"
   ```

### Performance Tips

1. **Large Files**: Processing may take time for large PDFs
2. **Image Processing**: Requires vision model access (full version only)
3. **Table Processing**: May be slow for complex tables
4. **Memory Usage**: Large documents may require more memory

## 📈 Output Examples

### Text Query Output
```
🔍 Text Query: What is the main topic?
--------------------------------------------------
Found 12 relevant text segments:

1. Score: 0.03564453125
   Text: 中华人民共和国刑事诉讼法...
   Source: xingshisusongfa.pdf
   Page: 1
```

### Table Query Output
```
📊 Table Query: What data is shown?
--------------------------------------------------
Found 1 relevant tables:

1. Score: 0.88
   Description: 该表格详细列出了各种统计数据，包括数量和百分比...
   Source: table_extraction_example.pdf
   Page: 2
```

### Image Query Output (Full Version)
```
🖼️ Image Query: What images are shown?
--------------------------------------------------
Found 2 relevant images:

1. Score: 0.92
   Description: 图片展示了一个流程图，说明了刑事诉讼的基本程序...
   Source: image_extraction_example.pdf
   Page: 3
```

## 🎉 Ready to Use!

The PDF RAG Demo provides a complete solution for querying PDF documents with natural language. Choose the version that best fits your needs:

- **Simplified Version**: Perfect for testing and basic text/table queries
- **Full Version**: Complete multi-modal analysis with image processing

**Start with the simplified version to test the system, then upgrade to the full version for advanced features!** 🚀

## 🔄 Version Comparison

| Feature | Simplified | Full Version |
|---------|------------|--------------|
| Text Processing | ✅ | ✅ |
| Table Processing | ✅ | ✅ |
| Image Processing | ❌ | ✅ |
| Multi-Modal Queries | ❌ | ✅ |
| OpenAI API Required | ❌ | ✅ |
| Setup Complexity | Low | Medium |
| Best For | Testing, Basic Use | Production, Advanced Use |
