#!/usr/bin/env python3
"""
PDF RAG Demo - Simplified version without vision model dependency
This version focuses on text and table processing without requiring OpenAI API for images
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from document_process import process_pdf
from image_table import extract_tables_from_pdf
from retrieve_documents import elastic_search, rerank
from es_functions import create_elastic_index
from config import get_es

class SimplePDFRAGDemo:
    def __init__(self):
        self.index_name = "simple_pdf_index"
        self.processed_files = {}
        
    def setup_pdf_rag(self):
        """
        Set up the PDF RAG system
        """
        print("=== Setting up Simple PDF RAG System ===\n")
        
        # Create Elasticsearch index
        print(f"1. Creating Elasticsearch index: {self.index_name}")
        try:
            create_elastic_index(self.index_name)
            print("✅ Index created successfully")
        except Exception as e:
            print(f"⚠️  Index creation failed (might already exist): {e}")
        
        return self.index_name
    
    def process_pdf_file(self, pdf_path: str, process_tables: bool = True):
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
            'tables': [],
            'file_path': pdf_path
        }
        
        try:
            # 1. Process text content
            print("📄 Processing text content...")
            process_pdf(self.index_name, pdf_path)
            results['text_processed'] = True
            print("✅ Text processing completed")
            
            # 2. Process tables (if requested)
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
    
    def _store_tables_in_elasticsearch(self, table_results: List[Dict], file_name: str):
        """
        Store table descriptions in Elasticsearch for querying
        """
        from embedding import local_embedding
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
    
    def query_table_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query table content from processed PDFs
        """
        print(f"\n📊 Table Query: {query}")
        print("-" * 50)
        
        try:
            # Search for relevant content
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
            print(f"   Tables extracted: {len(results['tables'])}")
        
        return self.processed_files

def main():
    """
    Main function to run the simple PDF RAG demo
    """
    print("📄 Simple PDF RAG Demo (Text + Tables)")
    print("=" * 50)
    
    # Initialize demo
    demo = SimplePDFRAGDemo()
    
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
        
        # Table queries
        table_queries = [
            "What tables are in the document?",
            "What data do the tables show?",
            "What information is presented in tables?"
        ]
        
        print("\n📊 Table Content Queries:")
        for query in table_queries:
            demo.query_table_content(query, top_k=3)
        
        # Step 5: Interactive mode
        print("\n" + "="*80)
        response = input("Would you like to enter interactive query mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n=== Interactive Query Mode ===")
            print("Enter your queries. Type 'quit' to exit.")
            
            while True:
                try:
                    query = input("\n📝 Your query: ").strip()
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        print("Goodbye!")
                        break
                    
                    if not query:
                        continue
                    
                    # Determine query type
                    query_lower = query.lower()
                    
                    if any(word in query_lower for word in ['table', 'data', 'chart', 'statistics']):
                        demo.query_table_content(query)
                    else:
                        demo.query_text_content(query)
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error processing query: {e}")
        
        print("\n✅ Simple PDF RAG demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
