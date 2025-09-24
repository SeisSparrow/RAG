# 📄 PDF RAG Demo - Complete Usage Guide

This guide shows you how to use the PDF RAG demo scripts to easily query PDF documents for text, images, and tables.

## 🎯 Overview

The PDF RAG Demo provides two main interfaces:
1. **`pdf_rag_demo.py`** - Complete interactive demo with full features
2. **`pdf_query.py`** - Simple command-line interface for quick queries

## 🚀 Quick Start

### Option 1: Simple Command-Line Interface

```bash
# Basic usage
python3 pdf_query.py <pdf_file> <query>

# Examples
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are shown?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What data is in the tables?"
```

### Option 2: Complete Interactive Demo

```bash
# Run the full demo
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
- **Vision Model**: For image analysis (optional)

## 🔧 Usage Examples

### Text Queries

```bash
# Query about document content
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What are the key principles?"
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What procedures are discussed?"
```

### Image Queries

```bash
# Query about images (use keywords like 'image', 'picture', 'figure')
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are in the document?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What do the pictures show?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What figures are displayed?"
```

### Table Queries

```bash
# Query about tables (use keywords like 'table', 'data', 'chart')
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What tables are in the document?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What data is shown in tables?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What statistics are presented?"
```

### Multi-Modal Queries

```bash
# Query about relationships (use keywords like 'relationship', 'together', 'both')
python3 pdf_query.py test_pdf/image_extraction_example.pdf "How do images and text relate?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "How do tables and text work together?"
```

## 🎮 Interactive Demo Features

When you run `python3 pdf_rag_demo.py`, you get:

### 1. Automatic File Processing
- Processes text content automatically
- Extracts and analyzes images (if present)
- Extracts and analyzes tables (if present)
- Shows processing summary

### 2. Example Queries
The demo runs example queries for each content type:
- **Text queries**: Document content analysis
- **Image queries**: Visual content analysis
- **Table queries**: Data analysis
- **Multi-modal queries**: Cross-content analysis

### 3. Interactive Mode
After running examples, you can enter interactive mode to ask your own questions.

## 📊 Query Types and Keywords

### Text Queries (Default)
- General questions about document content
- No specific keywords needed
- Examples: "What is the main topic?", "What are the key points?"

### Image Queries
**Keywords**: `image`, `picture`, `photo`, `figure`, `diagram`
- Examples: "What images are shown?", "What do the pictures depict?"

### Table Queries
**Keywords**: `table`, `chart`, `data`, `statistics`, `numbers`
- Examples: "What tables are present?", "What data is shown?"

### Multi-Modal Queries
**Keywords**: `relationship`, `relate`, `together`, `combine`, `both`
- Examples: "How do images and text relate?", "What's the relationship between tables and text?"

## 🔍 Advanced Usage

### Custom Processing Options

You can modify the `pdf_rag_demo.py` to customize processing:

```python
# Process only text (skip images and tables)
demo.process_pdf_file(pdf_path, process_images=False, process_tables=False)

# Process only text and images (skip tables)
demo.process_pdf_file(pdf_path, process_tables=False)
```

### Batch Processing

```python
# Process multiple files
pdf_files = [
    'test_pdf/xingshisusongfa.pdf',
    'test_pdf/image_extraction_example.pdf',
    'test_pdf/table_extraction_example.pdf'
]

for pdf_file in pdf_files:
    demo.process_pdf_file(pdf_file)
```

### Custom Queries

```python
# Use the demo class directly
demo = PDFRAGDemo()
demo.setup_pdf_rag()
demo.process_pdf_file('your_file.pdf')

# Query specific content types
text_results = demo.query_text_content("Your text query")
image_results = demo.query_image_content("Your image query")
table_results = demo.query_table_content("Your table query")
multimodal_results = demo.query_multimodal_content("Your multimodal query")
```

## 📁 File Structure

```
RAG_Demo/
├── pdf_rag_demo.py          # Complete interactive demo
├── pdf_query.py             # Simple command-line interface
├── document_process.py      # Text processing
├── image_table.py           # Image and table processing
├── retrieve_documents.py    # Query and retrieval
├── es_functions.py          # Elasticsearch operations
├── config.py                # Configuration
└── test_pdf/                # Example PDF files
    ├── xingshisusongfa.pdf
    ├── image_extraction_example.pdf
    └── table_extraction_example.pdf
```

## 🎯 Example Workflows

### Workflow 1: Legal Document Analysis
```bash
# Process legal document
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What is the main topic?"
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What are the key principles?"
python3 pdf_query.py test_pdf/xingshisusongfa.pdf "What procedures are described?"
```

### Workflow 2: Image-Rich Document Analysis
```bash
# Process image-rich document
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What images are shown?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "What do the figures illustrate?"
python3 pdf_query.py test_pdf/image_extraction_example.pdf "How do images support the text?"
```

### Workflow 3: Data-Rich Document Analysis
```bash
# Process table-rich document
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What tables are present?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What data is shown?"
python3 pdf_query.py test_pdf/table_extraction_example.pdf "What statistics are presented?"
```

## 🔧 Troubleshooting

### Common Issues

1. **File Not Found**
   ```bash
   # Check if file exists
   ls -la test_pdf/
   
   # Use absolute path if needed
   python3 pdf_query.py /full/path/to/your/file.pdf "Your query"
   ```

2. **Elasticsearch Connection Error**
   ```bash
   # Check Elasticsearch status
   curl -X GET "localhost:9200/"
   
   # Update config.py if needed
   ```

3. **Processing Errors**
   ```bash
   # Check file permissions
   ls -la your_file.pdf
   
   # Try with a different PDF file
   python3 pdf_query.py test_pdf/xingshisusongfa.pdf "Test query"
   ```

### Performance Tips

1. **Large Files**: Processing may take time for large PDFs
2. **Image Processing**: Requires vision model access
3. **Table Processing**: May be slow for complex tables
4. **Memory Usage**: Large documents may require more memory

## 📈 Output Examples

### Text Query Output
```
🔍 Text Query: What is the main topic?
--------------------------------------------------
Found 3 relevant text segments:

1. Score: 0.95
   Text: 刑事诉讼法是规范刑事诉讼程序的法律...
   Source: xingshisusongfa.pdf
   Page: 1
```

### Image Query Output
```
🖼️ Image Query: What images are shown?
--------------------------------------------------
Found 2 relevant images:

1. Score: 0.92
   Description: 图片展示了一个流程图，说明了刑事诉讼的基本程序...
   Source: image_extraction_example.pdf
   Page: 3
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

## 🎉 Ready to Use!

The PDF RAG Demo provides a complete solution for querying PDF documents with natural language. Whether you need to analyze legal documents, extract information from reports, or understand complex data presentations, the demo makes it easy to get started.

**Start with simple queries and explore the full capabilities!** 🚀
