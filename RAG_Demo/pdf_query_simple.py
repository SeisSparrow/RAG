#!/usr/bin/env python3
"""
Simple PDF Query Interface - Text and Tables Only
Quick and easy way to query PDF files for text and tables without vision model dependency.
"""

import sys
import os
from pdf_rag_demo_simple import SimplePDFRAGDemo

def main():
    """
    Simple command-line interface for PDF querying (text and tables only)
    """
    if len(sys.argv) < 3:
        print("Usage: python3 pdf_query_simple.py <pdf_file> <query>")
        print("\nExamples:")
        print("  python3 pdf_query_simple.py test_pdf/xingshisusongfa.pdf 'What is the main topic?'")
        print("  python3 pdf_query_simple.py test_pdf/table_extraction_example.pdf 'What data is in the tables?'")
        print("\nQuery types:")
        print("  - Text queries: Ask about document content")
        print("  - Table queries: Ask about tables (use words like 'table', 'data', 'chart')")
        print("\nNote: This version does not require OpenAI API key and focuses on text and table processing.")
        return
    
    pdf_file = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
    
    print(f"📄 Simple PDF Query Tool (Text + Tables)")
    print(f"File: {pdf_file}")
    print(f"Query: {query}")
    print("=" * 60)
    
    # Initialize demo
    demo = SimplePDFRAGDemo()
    
    try:
        # Setup
        demo.setup_pdf_rag()
        
        # Process PDF
        print(f"\n🔄 Processing PDF file...")
        success = demo.process_pdf_file(pdf_file)
        
        if not success:
            print("❌ Failed to process PDF file")
            return
        
        # Query content
        print(f"\n🔍 Querying content...")
        
        # Determine query type
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['table', 'chart', 'data', 'statistics', 'numbers']):
            demo.query_table_content(query)
        else:
            # Default to text query
            demo.query_text_content(query)
        
        print(f"\n✅ Query completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
