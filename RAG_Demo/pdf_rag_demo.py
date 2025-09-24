#!/usr/bin/env python3
"""
PDF RAG Demo - Complete pipeline for processing and querying PDF content
This script demonstrates how to use the RAG framework for PDF document analysis
including text, images, and tables.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from document_process import process_pdf
from image_table import extract_images_from_pdf, extract_tables_from_pdf
from retrieve_documents import elastic_search, rerank, rag_fusion, query_decompositon
from es_functions import create_elastic_index, delete_elastic_index
from config import get_es

class PDFRAGDemo:
    def __init__(self):
        self.index_name = "pdf_rag_index"
        self.processed_files = {}
        
    def setup_pdf_rag(self):
        """
        Set up the complete PDF RAG system
        """
        print("=== Setting up PDF RAG System ===\n")
        
        # 1. Create Elasticsearch index for PDF content
        print(f"1. Creating Elasticsearch index: {self.index_name}")
        try:
            create_elastic_index(self.index_name)
            print("✅ Index created successfully")
        except Exception as e:
            print(f"⚠️  Index creation failed (might already exist): {e}")
        
        return self.index_name
    
    def process_pdf_file(self, pdf_path: str, process_images: bool = True, process_tables: bool = True):
        """
        Process PDF file and store in vector database
        """
        print(f"\n=== Processing PDF File: {pdf_path} ===\n")
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False
        
        file_name = os.path.basename(pdf_path)
        results = {
            'text_processed': False,
            'images': [],
            'tables': [],
            'file_path': pdf_path
        }
        
        try:
            # 1. Process text content
            print("📄 Processing text content...")
            process_pdf(self.index_name, pdf_path)
            results['text_processed'] = True
            print("✅ Text processing completed")
            
            # 2. Process images (if requested)
            if process_images:
                print("\n🖼️ Processing images...")
                try:
                    image_results = extract_images_from_pdf(pdf_path)
                    results['images'] = image_results
                    print(f"✅ Extracted {len(image_results)} images")
                    
                    # Store image descriptions in Elasticsearch
                    self._store_images_in_elasticsearch(image_results, file_name)
                    
                    # Show sample image results
                    for i, result in enumerate(image_results[:3]):
                        print(f"   Image {i+1}: Page {result['page_num']+1}")
                        print(f"   Description: {result['summary'][:100]}...")
                except Exception as e:
                    print(f"⚠️ Image processing failed: {e}")
            
            # 3. Process tables (if requested)
            if process_tables:
                print("\n📊 Processing tables...")
                try:
                    table_results = extract_tables_from_pdf(pdf_path)
                    results['tables'] = table_results
                    print(f"✅ Extracted {len(table_results)} tables")
                    
                    # Store table descriptions in Elasticsearch
                    self._store_tables_in_elasticsearch(table_results, file_name)
                    
                    # Show sample table results
                    for i, result in enumerate(table_results[:3]):
                        print(f"   Table {i+1}: Page {result['page_num']+1}")
                        print(f"   Description: {result['context_augmented_table'][:100]}...")
                except Exception as e:
                    print(f"⚠️ Table processing failed: {e}")
            
            # Store results
            self.processed_files[file_name] = results
            print(f"\n✅ Successfully processed {file_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to process PDF file: {e}")
            return False
    
    def _store_images_in_elasticsearch(self, image_results: List[Dict], file_name: str):
        """
        Store image descriptions in Elasticsearch for querying
        """
        from embedding import local_embedding
        from config import get_es
        import time
        
        es = get_es()
        
        for i, result in enumerate(image_results):
            try:
                # Create text content for embedding
                image_text = f"Image on page {result['page_num']+1}: {result['context_augmented_summary']}"
                
                # Generate embedding
                embeddings = local_embedding([image_text])
                
                # Create metadata
                metadata = {
                    "file_type": "image",
                    "file_name": file_name,
                    "page": result['page_num'] + 1,
                    "image_index": result['image_index'],
                    "image_path": result.get('image_path', ''),
                    "page_context": result.get('page_context', '')[:500]  # Truncate for storage
                }
                
                body = {
                    'text': image_text,
                    'vector': embeddings[0],
                    'metadata': metadata,
                    'file_id': hash(file_name),
                    'image_id': f"{file_name}_{result['page_num']}_{result['image_index']}"
                }
                
                # Store in Elasticsearch
                retry = 0
                while retry <= 3:
                    try:
                        es.index(index=self.index_name, body=body)
                        break
                    except Exception as e:
                        print(f'[Elastic Error] {str(e)} retry')
                        retry += 1
                        time.sleep(1)
                        
            except Exception as e:
                print(f"Error storing image {i+1}: {e}")
                continue
    
    def _store_tables_in_elasticsearch(self, table_results: List[Dict], file_name: str):
        """
        Store table descriptions in Elasticsearch for querying
        """
        from embedding import local_embedding
        from config import get_es
        import time
        
        es = get_es()
        
        for i, result in enumerate(table_results):
            try:
                # Create text content for embedding
                table_text = f"Table on page {result['page_num']+1}: {result['context_augmented_table']}"
                
                # Generate embedding
                embeddings = local_embedding([table_text])
                
                # Create metadata
                metadata = {
                    "file_type": "table",
                    "file_name": file_name,
                    "page": result['page_num'] + 1,
                    "table_index": result['table_index'],
                    "table_markdown": result.get('table_markdown', '')[:1000],  # Truncate for storage
                    "page_context": result.get('page_context', '')[:500]  # Truncate for storage
                }
                
                body = {
                    'text': table_text,
                    'vector': embeddings[0],
                    'metadata': metadata,
                    'file_id': hash(file_name),
                    'image_id': None  # Not applicable for tables
                }
                
                # Store in Elasticsearch
                retry = 0
                while retry <= 3:
                    try:
                        es.index(index=self.index_name, body=body)
                        break
                    except Exception as e:
                        print(f'[Elastic Error] {str(e)} retry')
                        retry += 1
                        time.sleep(1)
                        
            except Exception as e:
                print(f"Error storing table {i+1}: {e}")
                continue
    
    def query_text_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query text content from processed PDFs
        """
        print(f"\n🔍 Text Query: {query}")
        print("-" * 50)
        
        try:
            # Search for relevant content
            results = elastic_search(query, self.index_name)
            
            if not results:
                print("No relevant text content found.")
                return []
            
            # Rerank results for better quality
            reranked_results = rerank(query, results)
            
            # Display top results
            print(f"Found {len(reranked_results)} relevant text segments:")
            for i, result in enumerate(reranked_results[:top_k]):
                print(f"\n{i+1}. Score: {result.get('score', 'N/A')}")
                print(f"   Text: {result['text'][:300]}...")
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"   Source: {metadata.get('file_name', 'Unknown')}")
                    if metadata.get('page'):
                        print(f"   Page: {metadata['page']}")
            
            return reranked_results[:top_k]
            
        except Exception as e:
            print(f"Error querying text content: {e}")
            return []
    
    def query_image_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query image content from processed PDFs
        """
        print(f"\n🖼️ Image Query: {query}")
        print("-" * 50)
        
        try:
            # Search for relevant content (images are stored as text descriptions)
            results = elastic_search(query, self.index_name)
            
            if not results:
                print("No relevant image content found.")
                return []
            
            # Filter for image-related results
            image_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if metadata and metadata.get('file_type') == 'image':
                    image_results.append(result)
            
            if not image_results:
                print("No image content found in search results.")
                return []
            
            # Rerank results
            reranked_results = rerank(query, image_results)
            
            # Display top results
            print(f"Found {len(reranked_results)} relevant images:")
            for i, result in enumerate(reranked_results[:top_k]):
                print(f"\n{i+1}. Score: {result.get('score', 'N/A')}")
                print(f"   Description: {result['text'][:300]}...")
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"   Source: {metadata.get('file_name', 'Unknown')}")
                    print(f"   Page: {metadata.get('page', 'Unknown')}")
            
            return reranked_results[:top_k]
            
        except Exception as e:
            print(f"Error querying image content: {e}")
            return []
    
    def query_table_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query table content from processed PDFs
        """
        print(f"\n📊 Table Query: {query}")
        print("-" * 50)
        
        try:
            # Search for relevant content (tables are stored as text descriptions)
            results = elastic_search(query, self.index_name)
            
            if not results:
                print("No relevant table content found.")
                return []
            
            # Filter for table-related results
            table_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if metadata and metadata.get('file_type') == 'table':
                    table_results.append(result)
            
            if not table_results:
                print("No table content found in search results.")
                return []
            
            # Rerank results
            reranked_results = rerank(query, table_results)
            
            # Display top results
            print(f"Found {len(reranked_results)} relevant tables:")
            for i, result in enumerate(reranked_results[:top_k]):
                print(f"\n{i+1}. Score: {result.get('score', 'N/A')}")
                print(f"   Description: {result['text'][:300]}...")
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"   Source: {metadata.get('file_name', 'Unknown')}")
                    print(f"   Page: {metadata.get('page', 'Unknown')}")
            
            return reranked_results[:top_k]
            
        except Exception as e:
            print(f"Error querying table content: {e}")
            return []
    
    def query_multimodal_content(self, query: str, top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Query all content types (text, images, tables) from processed PDFs
        """
        print(f"\n🔗 Multi-Modal Query: {query}")
        print("=" * 60)
        
        results = {
            'text': self.query_text_content(query, top_k),
            'images': self.query_image_content(query, top_k),
            'tables': self.query_table_content(query, top_k)
        }
        
        # Summary
        total_results = sum(len(content_type) for content_type in results.values())
        print(f"\n📈 Query Summary:")
        print(f"   Text results: {len(results['text'])}")
        print(f"   Image results: {len(results['images'])}")
        print(f"   Table results: {len(results['tables'])}")
        print(f"   Total results: {total_results}")
        
        return results
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get summary of all processed files
        """
        print("\n📈 Processing Summary")
        print("=" * 50)
        
        if not self.processed_files:
            print("No files processed yet.")
            return {}
        
        for file_name, results in self.processed_files.items():
            print(f"\n📄 {file_name}:")
            print(f"   Text processed: {'✅' if results['text_processed'] else '❌'}")
            print(f"   Images extracted: {len(results['images'])}")
            print(f"   Tables extracted: {len(results['tables'])}")
        
        return self.processed_files
    
    def interactive_queries(self):
        """
        Interactive query interface
        """
        print(f"\n=== Interactive PDF Query Interface ===\n")
        print("Enter your queries about the PDF content. Type 'quit' to exit.")
        print("Query types:")
        print("  - Text queries: Ask about document content")
        print("  - Image queries: Ask about images in the document")
        print("  - Table queries: Ask about tables in the document")
        print("  - Multi-modal queries: Ask about relationships between content types")
        print()
        print("Example queries:")
        print("  - 'What is the main topic of this document?'")
        print("  - 'What images are in the document?'")
        print("  - 'What tables show data?'")
        print("  - 'How do images and text relate to each other?'")
        print()
        
        while True:
            try:
                query = input("📝 Your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Determine query type based on keywords
                query_lower = query.lower()
                
                if any(word in query_lower for word in ['image', 'picture', 'photo', 'figure', 'diagram']):
                    self.query_image_content(query)
                elif any(word in query_lower for word in ['table', 'chart', 'data', 'statistics', 'numbers']):
                    self.query_table_content(query)
                elif any(word in query_lower for word in ['relationship', 'relate', 'together', 'combine', 'both']):
                    self.query_multimodal_content(query)
                else:
                    # Default to text query
                    self.query_text_content(query)
                
                print("\n" + "="*80 + "\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error processing query: {e}")

def main():
    """
    Main function to run the PDF RAG demo
    """
    print("📄 PDF RAG System Demo")
    print("=" * 50)
    
    # Initialize demo
    demo = PDFRAGDemo()
    
    try:
        # Step 1: Setup
        demo.setup_pdf_rag()
        
        # Step 2: Get PDF file from user
        print("\n📁 Available PDF files:")
        test_pdf_dir = "test_pdf"
        if os.path.exists(test_pdf_dir):
            pdf_files = [f for f in os.listdir(test_pdf_dir) if f.endswith('.pdf')]
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf_file}")
        
        print("\nEnter PDF file path (or press Enter for default):")
        pdf_input = input("PDF file: ").strip()
        
        if not pdf_input:
            # Use default files
            default_files = [
                'test_pdf/xingshisusongfa.pdf',
                'test_pdf/image_extraction_example.pdf',
                'test_pdf/table_extraction_example.pdf'
            ]
            
            for pdf_file in default_files:
                if os.path.exists(pdf_file):
                    print(f"\n🔄 Processing default file: {pdf_file}")
                    demo.process_pdf_file(pdf_file)
        else:
            # Process user-specified file
            if not os.path.exists(pdf_input):
                print(f"❌ File not found: {pdf_input}")
                return
            
            demo.process_pdf_file(pdf_input)
        
        # Step 3: Show processing summary
        demo.get_processing_summary()
        
        # Step 4: Run example queries
        print(f"\n=== Running Example Queries ===\n")
        
        # Text queries
        text_queries = [
            "What is the main topic of this document?",
            "What are the key points discussed?",
            "What are the main concepts?"
        ]
        
        print("📝 Text Content Queries:")
        for query in text_queries:
            demo.query_text_content(query, top_k=3)
        
        # Image queries
        image_queries = [
            "What images are in the document?",
            "What do the images show?",
            "What is depicted in the figures?"
        ]
        
        print("\n🖼️ Image Content Queries:")
        for query in image_queries:
            demo.query_image_content(query, top_k=3)
        
        # Table queries
        table_queries = [
            "What tables are in the document?",
            "What data do the tables show?",
            "What information is presented in tables?"
        ]
        
        print("\n📊 Table Content Queries:")
        for query in table_queries:
            demo.query_table_content(query, top_k=3)
        
        # Multi-modal queries
        multimodal_queries = [
            "How do images and text relate to each other?",
            "What is the relationship between tables and text?",
            "How do visual elements support the main content?"
        ]
        
        print("\n🔗 Multi-Modal Queries:")
        for query in multimodal_queries:
            demo.query_multimodal_content(query, top_k=3)
        
        # Step 5: Interactive mode
        print("\n" + "="*80)
        response = input("Would you like to enter interactive query mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            demo.interactive_queries()
        
        print("\n✅ PDF RAG demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
