"""
Test script for document processing functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.document_processor import DocumentProcessor
from app.services.document_storage import DocumentStorageService


async def test_document_processing():
    """Test document processing with sample data"""
    
    processor = DocumentProcessor()
    storage = DocumentStorageService()
    
    # Test with sample text content
    sample_text = """
CONTRACT AGREEMENT

ARTICLE 1: DEFINITIONS

For purposes of this Agreement, the following terms shall have the meanings set forth below:

(a) "Agreement" means this Contract Agreement and all amendments and modifications hereto.

(b) "Party" means each of the signatories to this Agreement.

(c) "Effective Date" means the date on which this Agreement becomes effective.

ARTICLE 2: OBLIGATIONS

Each Party agrees to perform the following obligations:

1. Comply with all applicable laws and regulations.

2. Maintain confidentiality of all proprietary information.

3. Provide written notice of any material changes.

ARTICLE 3: TERMINATION

This Agreement may be terminated by either Party upon thirty (30) days written notice.
"""
    
    try:
        print("🧪 Testing document processing...")
        
        # Process the sample document
        processed_doc = await processor.process_document(
            file_content=sample_text.encode('utf-8'),
            filename="sample_contract.txt",
            document_id="test-doc-123",
            file_type="txt"
        )
        
        print(f"✅ Document processed successfully!")
        print(f"   - Total chunks: {len(processed_doc.chunks)}")
        print(f"   - Content length: {len(processed_doc.content)}")
        
        # Display chunk information
        print("\n📄 Document chunks:")
        for i, chunk in enumerate(processed_doc.chunks[:5]):  # Show first 5 chunks
            print(f"   {i+1}. [{chunk.chunk_type}] {chunk.text[:50]}...")
            print(f"      Position: page {chunk.position.page_number}, para {chunk.position.paragraph_index}")
            print(f"      Characters: {chunk.position.char_start}-{chunk.position.char_end}")
            print()
        
        if len(processed_doc.chunks) > 5:
            print(f"   ... and {len(processed_doc.chunks) - 5} more chunks")
        
        print(f"\n📊 Processing stats: {processed_doc.processing_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False


async def test_pdf_processing():
    """Test PDF processing if sample PDF is available"""
    try:
        # Check if sample PDF exists
        sample_pdf_path = Path("sample_documents/sample_contract.pdf")
        if not sample_pdf_path.exists():
            print("⚠️  No sample PDF found, skipping PDF test")
            return True
        
        processor = DocumentProcessor()
        
        with open(sample_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        print("🧪 Testing PDF processing...")
        
        processed_doc = await processor.process_document(
            file_content=pdf_content,
            filename="sample_contract.pdf",
            document_id="test-pdf-123",
            file_type="pdf"
        )
        
        print(f"✅ PDF processed successfully!")
        print(f"   - Total chunks: {len(processed_doc.chunks)}")
        print(f"   - Processing stats: {processed_doc.processing_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF testing: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting document processing tests...\n")
    
    # Run tests
    success = asyncio.run(test_document_processing())
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
