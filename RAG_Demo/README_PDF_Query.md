# 📄 PDF Query System - RAG Framework

This guide shows you how to use the RAG (Retrieval Augmented Generation) framework to query PDF documents, specifically using the example file `test_pdf/xingshisusongfa.pdf`.

## 🎯 Overview

The PDF Query System allows you to:
- Process PDF documents and extract text content
- Create embeddings for semantic search
- Query documents using natural language
- Get precise answers with source references
- Use advanced techniques like hybrid search and reranking

## 🏗️ System Architecture

```
PDF Document → Text Extraction → Chunking → Embeddings → Vector Database → Query Processing → Response
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
- **Embedding Service**: Configured in `config.py`
- **Reranking Service**: Optional, for improved results

## 🚀 Quick Start

### Step 1: Create Elasticsearch Index
```bash
python3 -c "from es_functions import create_elastic_index; create_elastic_index('pdf_index')"
```

### Step 2: Process PDF Document
```bash
# Process the example PDF file
python3 -c "
from document_process import process_pdf
process_pdf('pdf_index', 'test_pdf/xingshisusongfa.pdf')
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

The `document_process.py` module handles PDF processing:

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

### 2. Document Querying

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

Here are example queries you can try with the `xingshisusongfa.pdf` document:

### Basic Content Queries
```python
queries = [
    "什么是刑事诉讼法？",
    "刑事诉讼法的基本原则有哪些？",
    "什么是无罪推定原则？",
    "刑事诉讼程序包括哪些阶段？",
    "什么是证据的合法性？"
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

```python
#!/usr/bin/env python3
"""
Complete PDF Query Workflow Example
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

## 📚 Additional Resources

- **RAG Framework**: Based on the Retrieval Augmented Generation pattern
- **Elasticsearch**: Vector database for document storage and retrieval
- **PyMuPDF**: PDF text extraction and processing
- **Jieba**: Chinese text segmentation for keyword search
- **OpenAI Embeddings**: Semantic vector generation

## 🤝 Contributing

To extend the PDF query system:

1. Add new document types in `document_process.py`
2. Implement custom chunking strategies
3. Add domain-specific query enhancement
4. Integrate additional embedding models
5. Implement custom reranking algorithms

---

**Ready to query your PDF documents with the power of RAG!** 🚀
