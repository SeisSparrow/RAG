# 📄 PDF Query System - RAG Framework

This guide shows you how to use the RAG (Retrieval Augmented Generation) framework to query PDF documents, specifically using the example file `test_pdf/xingshisusongfa.pdf`.

## 🎯 Overview

The PDF Query System allows you to:
- Process PDF documents and extract text content
- **Extract and analyze images from PDFs**
- **Extract and query tables from PDFs**
- Create embeddings for semantic search
- Query documents using natural language
- Get precise answers with source references
- Use advanced techniques like hybrid search and reranking

## 🏗️ System Architecture

```
PDF Document → Text/Image/Table Extraction → Chunking → Embeddings → Vector Database → Query Processing → Response
```

### Multi-Modal Processing Pipeline
- **Text**: Direct extraction and chunking
- **Images**: Extract → Visual Analysis → Context Augmentation → Text Description
- **Tables**: Extract → Markdown Conversion → Context Augmentation → Structured Description

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
- **Embedding Service**: Configured in `config.py`
- **Reranking Service**: Optional, for improved results

## 🚀 Quick Start

### Step 1: Create Elasticsearch Index
```bash
python3 -c "from es_functions import create_elastic_index; create_elastic_index('pdf_index')"
```

### Step 2: Process PDF Document
```bash
# Process the example PDF file (text content)
python3 -c "
from document_process import process_pdf
process_pdf('pdf_index', 'test_pdf/xingshisusongfa.pdf')
"

# Extract and process images from PDF
python3 -c "
from image_table import extract_images_from_pdf
results = extract_images_from_pdf('test_pdf/image_extraction_example.pdf')
print(f'Extracted {len(results)} images')
"

# Extract and process tables from PDF
python3 -c "
from image_table import extract_tables_from_pdf
results = extract_tables_from_pdf('test_pdf/table_extraction_example.pdf')
print(f'Extracted {len(results)} tables')
"
```

### Step 3: Query the Document
```bash
python3 -c "
from retrieve_documents import elastic_search, rerank
query = '什么是刑事诉讼法的基本原则？'
results = elastic_search(query, 'pdf_index')
print('Search Results:')
for i, result in enumerate(results[:3]):
    print(f'{i+1}. {result[\"text\"][:200]}...')
"
```

## 📖 Detailed Usage

### 1. Document Processing

The `document_process.py` module handles PDF text processing:

```python
from document_process import process_pdf

# Process a PDF file
process_pdf(
    es_index='pdf_index',           # Elasticsearch index name
    file_path='test_pdf/xingshisusongfa.pdf'  # Path to PDF file
)
```

**What happens during processing:**
- PDF text extraction using PyMuPDF
- Text chunking (1024 tokens per chunk, 100 token overlap)
- Embedding generation for each chunk
- Storage in Elasticsearch with metadata

### 2. Image Processing

The `image_table.py` module handles image extraction and analysis:

```python
from image_table import extract_images_from_pdf, summarize_image, context_augmentation

# Extract images from PDF
results = extract_images_from_pdf('test_pdf/image_extraction_example.pdf')

# Process individual image
image_summary = summarize_image('path/to/image.png')

# Augment image description with context
augmented_description = context_augmentation(page_context, image_description)
```

**Image Processing Pipeline:**
- **Extraction**: Extract images from PDF pages
- **Filtering**: Remove small/background images
- **Analysis**: Use vision model to describe image content
- **Context Augmentation**: Enhance description using surrounding text
- **Storage**: Store descriptions with page references

**Example Image Processing:**
```python
# Extract all images from a PDF
pdf_path = 'test_pdf/image_extraction_example.pdf'
image_results = extract_images_from_pdf(pdf_path)

for result in image_results:
    print(f"Page {result['page_num'] + 1}, Image {result['image_index']}")
    print(f"Description: {result['summary']}")
    print(f"Context Augmented: {result['context_augmented_summary']}")
    print("-" * 50)
```

### 3. Table Processing

The `image_table.py` module also handles table extraction and analysis:

```python
from image_table import extract_tables_from_pdf, table_context_augmentation

# Extract tables from PDF
results = extract_tables_from_pdf('test_pdf/table_extraction_example.pdf')

# Process individual table
table_description = table_context_augmentation(page_context, table_markdown)
```

**Table Processing Pipeline:**
- **Detection**: Find tables in PDF pages
- **Extraction**: Convert tables to Markdown format
- **Context Analysis**: Analyze surrounding text for context
- **Description Generation**: Create natural language descriptions
- **Storage**: Store structured table data with descriptions

**Example Table Processing:**
```python
# Extract all tables from a PDF
pdf_path = 'test_pdf/table_extraction_example.pdf'
table_results = extract_tables_from_pdf(pdf_path)

for result in table_results:
    print(f"Page {result['page_num'] + 1}, Table {result['table_index']}")
    print(f"Markdown:\n{result['table_markdown']}")
    print(f"Description: {result['context_augmented_table']}")
    print("-" * 50)
```

### 4. Multi-Modal Document Processing

For comprehensive document analysis, you can process text, images, and tables together:

```python
from document_process import process_pdf
from image_table import extract_images_from_pdf, extract_tables_from_pdf

def process_complete_pdf(pdf_path, es_index):
    """Process PDF with text, images, and tables"""
    
    # 1. Process text content
    print("Processing text content...")
    process_pdf(es_index, pdf_path)
    
    # 2. Extract and process images
    print("Processing images...")
    image_results = extract_images_from_pdf(pdf_path)
    print(f"Extracted {len(image_results)} images")
    
    # 3. Extract and process tables
    print("Processing tables...")
    table_results = extract_tables_from_pdf(pdf_path)
    print(f"Extracted {len(table_results)} tables")
    
    return {
        'images': image_results,
        'tables': table_results
    }

# Example usage
results = process_complete_pdf('test_pdf/image_extraction_example.pdf', 'multimodal_index')
```

### 5. Document Querying

The `retrieve_documents.py` module provides advanced querying capabilities:

```python
from retrieve_documents import elastic_search, rerank, rag_fusion, query_decompositon

# Basic search
query = "刑事诉讼法的基本原则是什么？"
results = elastic_search(query, 'pdf_index')

# Enhanced search with reranking
reranked_results = rerank(query, results)

# Query decomposition for complex questions
sub_queries = query_decompositon("刑事诉讼法和民事诉讼法的区别是什么？")

# RAG Fusion for multiple query variations
fusion_queries = rag_fusion("什么是无罪推定原则？")
```

### 3. Advanced Query Techniques

#### Hybrid Search
Combines keyword search and semantic search:
```python
# The system automatically performs:
# 1. Keyword search using jieba segmentation
# 2. Vector similarity search
# 3. Reciprocal Rank Fusion (RRF) to combine results
```

#### Query Enhancement
```python
# Query decomposition for complex questions
complex_query = "刑事诉讼法和民事诉讼法的区别是什么？"
sub_queries = query_decompositon(complex_query)
# Returns: ["什么是刑事诉讼法？", "什么是民事诉讼法？", "刑事诉讼法和民事诉讼法的区别是什么？"]

# RAG Fusion for better coverage
fusion_queries = rag_fusion("无罪推定原则")
# Returns: ["什么是无罪推定原则？", "无罪推定原则的法律依据是什么？"]
```

#### Multi-turn Conversation
```python
# Coreference resolution for follow-up questions
chat_history = """
'user': 什么是刑事诉讼法？
'assistant': 刑事诉讼法是规范刑事诉讼程序的法律...
'user': 它的基本原则有哪些？
"""

resolved_query = coreference_resolution("它的基本原则有哪些？", chat_history)
# Returns: "刑事诉讼法的基本原则有哪些？"
```

## 🔍 Example Queries

### Text Content Queries (xingshisusongfa.pdf)
```python
queries = [
    "什么是刑事诉讼法？",
    "刑事诉讼法的基本原则有哪些？",
    "什么是无罪推定原则？",
    "刑事诉讼程序包括哪些阶段？",
    "什么是证据的合法性？"
]
```

### Image Content Queries (image_extraction_example.pdf)
```python
queries = [
    "文档中有哪些图片？",
    "图片展示了什么内容？",
    "图片中的文字是什么？",
    "图片说明了什么概念？",
    "图片和周围文字的关系是什么？"
]
```

### Table Content Queries (table_extraction_example.pdf)
```python
queries = [
    "文档中有哪些表格？",
    "表格显示了什么数据？",
    "表格的结构是什么？",
    "表格的用途是什么？",
    "表格中的数据说明了什么？"
]
```

### Multi-Modal Queries
```python
queries = [
    "文档中图片和表格的关系是什么？",
    "图片和文字如何相互补充？",
    "表格数据如何支持文档的主要观点？",
    "文档的视觉元素如何增强理解？"
]
```

### Comparative Queries
```python
queries = [
    "刑事诉讼法和民事诉讼法的区别是什么？",
    "公诉案件和自诉案件有什么不同？",
    "一审程序和二审程序的区别？"
]
```

### Specific Legal Concepts
```python
queries = [
    "什么是辩护权？",
    "犯罪嫌疑人有哪些权利？",
    "什么是强制措施？",
    "刑事诉讼中的证明标准是什么？"
]
```

## 📊 Query Results Format

Each query returns results with the following structure:

```python
{
    'id': 'document_chunk_id',
    'text': 'extracted text content',
    'file_id': 'file_identifier',
    'metadata': {
        'file_name': 'xingshisusongfa.pdf',
        'page': 1,
        'chunk_id': 0
    },
    'rank': 1,
    'score': 0.95  # Relevance score (if reranked)
}
```

## 🛠️ Configuration

### Elasticsearch Configuration
Edit `config.py` to match your Elasticsearch setup:

```python
class ElasticConfig:
    url = 'http://localhost:9200'  # Update with your credentials if needed

# Embedding service URLs
EMBEDDING_URL = "http://test.2brain.cn:9800/v1/emb"
RERANK_URL = "http://test.2brain.cn:2260/rerank"
```

### Text Processing Parameters
In `document_process.py`, you can adjust:

```python
# Chunk size and overlap
chunk_size = 1024        # Tokens per chunk
chunk_overlap = 100      # Overlap between chunks

# Batch size for embedding generation
batch_size = 25          # Process 25 chunks at a time
```

### Image Processing Parameters
In `image_table.py`, you can adjust:

```python
# Image filtering parameters
min_image_width = 200    # Minimum image width
min_image_height = 100   # Minimum image height
page_width_ratio = 3     # Image must be at least 1/3 of page width

# Vision model configuration
IMAGE_MODEL_URL = "http://test.2brain.cn:23333/v1"  # Vision model endpoint
model_name = "internvl-internlm2"                   # Vision model name
```

### Table Processing Parameters
In `image_table.py`, you can adjust:

```python
# Table extraction settings
table_detection_confidence = 0.8  # Confidence threshold for table detection
markdown_formatting = True        # Convert tables to Markdown
context_window = 1500            # Characters of context around tables
```

## 🎯 Best Practices

### 1. Query Formulation
- Use specific legal terms when possible
- Ask focused questions rather than broad ones
- Use comparative language for differences ("区别", "不同")
- Include context for ambiguous terms

### 2. Result Interpretation
- Check the relevance scores
- Look at multiple results for comprehensive answers
- Use reranking for better quality results
- Consider query decomposition for complex questions

### 3. Performance Optimization
- Use appropriate chunk sizes for your document type
- Batch embedding generation for efficiency
- Index multiple documents in the same index for cross-document queries

## 🔧 Troubleshooting

### Common Issues

1. **Elasticsearch Connection Error**
   ```bash
   # Check if Elasticsearch is running
   curl -X GET "localhost:9200/"
   
   # Update credentials in config.py if needed
   ```

2. **Embedding Service Error**
   ```bash
   # Test embedding service
   python3 -c "from embedding import local_embedding; print(local_embedding(['test']))"
   ```

3. **PDF Processing Error**
   ```bash
   # Check if PDF file exists and is readable
   ls -la test_pdf/xingshisusongfa.pdf
   ```

### Performance Issues

1. **Slow Processing**
   - Reduce chunk size
   - Increase batch size
   - Use faster embedding models

2. **Memory Issues**
   - Process documents in smaller batches
   - Reduce chunk overlap
   - Clear Elasticsearch cache

## 📈 Advanced Features

### 1. Multi-Document Queries
```python
# Process multiple PDFs into the same index
pdf_files = [
    'test_pdf/xingshisusongfa.pdf',
    'test_pdf/table_extraction_example.pdf',
    'test_pdf/image_extraction_example.pdf'
]

for pdf_file in pdf_files:
    process_pdf('multi_doc_index', pdf_file)
```

### 2. Metadata Filtering
```python
# Query with metadata filters
query = {
    "bool": {
        "must": [
            {"match": {"text": "刑事诉讼法"}},
            {"term": {"metadata.file_name": "xingshisusongfa.pdf"}}
        ]
    }
}
```

### 3. Custom Scoring
```python
# Adjust RRF parameters
def hybrid_search_rrf(keyword_hits, vector_hits, k=60):
    # k=60 is the RRF parameter, adjust for your needs
    # Lower k gives more weight to top results
```

## 🎉 Example Complete Workflow

### Text-Only Workflow
```python
#!/usr/bin/env python3
"""
Complete PDF Text Query Workflow Example
"""

from es_functions import create_elastic_index
from document_process import process_pdf
from retrieve_documents import elastic_search, rerank

def main():
    # 1. Create index
    index_name = 'legal_docs'
    create_elastic_index(index_name)
    
    # 2. Process PDF
    pdf_file = 'test_pdf/xingshisusongfa.pdf'
    process_pdf(index_name, pdf_file)
    
    # 3. Query examples
    queries = [
        "什么是刑事诉讼法？",
        "刑事诉讼法的基本原则有哪些？",
        "什么是无罪推定原则？"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 50)
        
        # Search
        results = elastic_search(query, index_name)
        
        # Rerank for better results
        reranked_results = rerank(query, results)
        
        # Display top results
        for i, result in enumerate(reranked_results[:3]):
            print(f"{i+1}. {result['text'][:200]}...")
            print(f"   Score: {result.get('score', 'N/A')}")
            print()

if __name__ == "__main__":
    main()
```

### Multi-Modal Workflow (Text + Images + Tables)
```python
#!/usr/bin/env python3
"""
Complete Multi-Modal PDF Query Workflow Example
"""

from es_functions import create_elastic_index
from document_process import process_pdf
from image_table import extract_images_from_pdf, extract_tables_from_pdf
from retrieve_documents import elastic_search, rerank

def process_multimodal_pdf(pdf_path, index_name):
    """Process PDF with all modalities"""
    
    print(f"🔄 Processing: {pdf_path}")
    print("=" * 60)
    
    # 1. Process text content
    print("📄 Processing text content...")
    process_pdf(index_name, pdf_path)
    print("✅ Text processing completed")
    
    # 2. Extract and process images
    print("\n🖼️ Processing images...")
    try:
        image_results = extract_images_from_pdf(pdf_path)
        print(f"✅ Extracted {len(image_results)} images")
        
        for i, result in enumerate(image_results[:3]):  # Show first 3
            print(f"   Image {i+1}: Page {result['page_num']+1}")
            print(f"   Description: {result['summary'][:100]}...")
    except Exception as e:
        print(f"⚠️ Image processing failed: {e}")
        image_results = []
    
    # 3. Extract and process tables
    print("\n📊 Processing tables...")
    try:
        table_results = extract_tables_from_pdf(pdf_path)
        print(f"✅ Extracted {len(table_results)} tables")
        
        for i, result in enumerate(table_results[:3]):  # Show first 3
            print(f"   Table {i+1}: Page {result['page_num']+1}")
            print(f"   Description: {result['context_augmented_table'][:100]}...")
    except Exception as e:
        print(f"⚠️ Table processing failed: {e}")
        table_results = []
    
    return {
        'images': image_results,
        'tables': table_results
    }

def query_multimodal_content(index_name, queries):
    """Query multimodal content"""
    
    print(f"\n🔍 Querying multimodal content...")
    print("=" * 60)
    
    for query in queries:
        print(f"\n🎯 Query: {query}")
        print("-" * 50)
        
        # Search
        results = elastic_search(query, index_name)
        
        # Rerank for better results
        reranked_results = rerank(query, results)
        
        # Display top results
        for i, result in enumerate(reranked_results[:3]):
            print(f"{i+1}. {result['text'][:200]}...")
            print(f"   Score: {result.get('score', 'N/A')}")
            print()

def main():
    # 1. Create index
    index_name = 'multimodal_docs'
    create_elastic_index(index_name)
    
    # 2. Process different PDF types
    pdf_files = [
        'test_pdf/xingshisusongfa.pdf',           # Text-heavy legal document
        'test_pdf/image_extraction_example.pdf',  # Image-rich document
        'test_pdf/table_extraction_example.pdf'   # Table-rich document
    ]
    
    all_results = {}
    
    for pdf_file in pdf_files:
        try:
            results = process_multimodal_pdf(pdf_file, index_name)
            all_results[pdf_file] = results
        except Exception as e:
            print(f"❌ Failed to process {pdf_file}: {e}")
    
    # 3. Query examples for different content types
    text_queries = [
        "什么是刑事诉讼法？",
        "刑事诉讼法的基本原则有哪些？"
    ]
    
    image_queries = [
        "文档中有哪些图片？",
        "图片展示了什么内容？"
    ]
    
    table_queries = [
        "文档中有哪些表格？",
        "表格显示了什么数据？"
    ]
    
    multimodal_queries = [
        "文档中图片和表格的关系是什么？",
        "图片和文字如何相互补充？"
    ]
    
    # 4. Run queries
    print(f"\n📝 Text Content Queries:")
    query_multimodal_content(index_name, text_queries)
    
    print(f"\n🖼️ Image Content Queries:")
    query_multimodal_content(index_name, image_queries)
    
    print(f"\n📊 Table Content Queries:")
    query_multimodal_content(index_name, table_queries)
    
    print(f"\n🔗 Multi-Modal Queries:")
    query_multimodal_content(index_name, multimodal_queries)
    
    # 5. Summary
    print(f"\n📈 Processing Summary:")
    print("=" * 60)
    for pdf_file, results in all_results.items():
        print(f"📄 {pdf_file}:")
        print(f"   Images: {len(results['images'])}")
        print(f"   Tables: {len(results['tables'])}")

if __name__ == "__main__":
    main()
```

## 📚 Additional Resources

### Core Technologies
- **RAG Framework**: Based on the Retrieval Augmented Generation pattern
- **Elasticsearch**: Vector database for document storage and retrieval
- **PyMuPDF**: PDF text extraction and processing
- **Jieba**: Chinese text segmentation for keyword search
- **OpenAI Embeddings**: Semantic vector generation

### Multi-Modal Technologies
- **Vision Models**: Image analysis and description generation
- **Table Detection**: Automatic table identification and extraction
- **Context Augmentation**: Enhanced descriptions using surrounding text
- **Markdown Conversion**: Structured table representation

### Processing Capabilities
- **Text**: Direct extraction, chunking, and embedding
- **Images**: Visual analysis, OCR, context-aware descriptions
- **Tables**: Structure detection, data extraction, natural language descriptions
- **Multi-Modal**: Cross-modal relationship analysis and querying

## 🤝 Contributing

To extend the PDF query system:

### Text Processing
1. Add new document types in `document_process.py`
2. Implement custom chunking strategies
3. Add domain-specific query enhancement
4. Integrate additional embedding models
5. Implement custom reranking algorithms

### Multi-Modal Processing
1. Add support for more image formats
2. Implement custom vision models
3. Add advanced table analysis features
4. Implement cross-modal relationship detection
5. Add support for mathematical formulas and equations

### Advanced Features
1. Implement document summarization
2. Add citation and reference tracking
3. Implement document comparison
4. Add temporal analysis for document versions
5. Implement collaborative filtering for similar documents

---

**Ready to query your PDF documents with the power of multi-modal RAG!** 🚀📄🖼️📊
