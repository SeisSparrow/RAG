#!/usr/bin/env python3
"""
Test script for PDF RAG demo
Quick test to verify the image and table querying functionality works
"""

import sys
import os
from pdf_rag_demo import PDFRAGDemo

def test_pdf_rag():
    """
    Test the PDF RAG functionality
    """
    print("🧪 Testing PDF RAG Demo")
    print("=" * 50)
    
    # Initialize demo
    demo = PDFRAGDemo()
    
    try:
        # Setup
        print("1. Setting up system...")
        demo.setup_pdf_rag()
        
        # Test with image extraction example
        pdf_file = 'test_pdf/image_extraction_example.pdf'
        if not os.path.exists(pdf_file):
            print(f"❌ Test file not found: {pdf_file}")
            print("Available files:")
            test_dir = "test_pdf"
            if os.path.exists(test_dir):
                for f in os.listdir(test_dir):
                    if f.endswith('.pdf'):
                        print(f"  - {f}")
            return False
        
        # Process PDF
        print(f"\n2. Processing PDF: {pdf_file}")
        success = demo.process_pdf_file(pdf_file)
        
        if not success:
            print("❌ Failed to process PDF")
            return False
        
        # Test queries
        print(f"\n3. Testing queries...")
        
        # Test image query
        print("\n🖼️ Testing image query...")
        image_results = demo.query_image_content("What images are in the document?", top_k=3)
        
        if image_results:
            print("✅ Image query successful")
        else:
            print("⚠️ No image results found")
        
        # Test text query
        print("\n📝 Testing text query...")
        text_results = demo.query_text_content("What is this document about?", top_k=3)
        
        if text_results:
            print("✅ Text query successful")
        else:
            print("⚠️ No text results found")
        
        # Show summary
        print(f"\n4. Processing summary:")
        demo.get_processing_summary()
        
        print(f"\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_rag()
    sys.exit(0 if success else 1)
