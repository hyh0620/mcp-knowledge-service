"""Integration tests for PDF Loader using real PDF files.

These tests use actual PDF files from fixtures/sample_documents to verify
end-to-end functionality of the PDF loader.
"""

from pathlib import Path

import pytest

from src.core.types import Document
from src.libs.loader.pdf_loader import PdfLoader


# Fixture paths
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_documents"
SIMPLE_PDF = FIXTURES_DIR / "simple.pdf"
COMPLEX_PDF = FIXTURES_DIR / "complex_technical_doc.pdf"


class TestPdfLoaderWithRealFiles:
    """Integration tests using real PDF files."""
    
    def test_simple_pdf_exists(self):
        """Verify test fixture exists."""
        assert SIMPLE_PDF.exists(), f"Test fixture not found: {SIMPLE_PDF}"
    
    def test_complex_pdf_exists(self):
        """Verify second test fixture exists."""
        assert COMPLEX_PDF.exists(), f"Test fixture not found: {COMPLEX_PDF}"
    
    def test_load_simple_pdf(self):
        """Load a simple text-only PDF and verify Document structure."""
        loader = PdfLoader()
        doc = loader.load(SIMPLE_PDF)
        
        # Verify Document structure
        assert isinstance(doc, Document)
        assert doc.id.startswith("doc_")
        assert len(doc.text) > 0
        
        # Verify required metadata
        assert doc.metadata["source_path"] == str(SIMPLE_PDF)
        assert doc.metadata["doc_type"] == "pdf"
        assert "doc_hash" in doc.metadata
        
        # Verify title extraction (the PDF has "Sample Document" as title)
        assert "title" in doc.metadata
        assert len(doc.metadata["title"]) > 0
        assert "sample" in doc.metadata["title"].lower() or "document" in doc.metadata["title"].lower()
        
        # Verify text content contains expected keywords
        assert "sample" in doc.text.lower() or "test" in doc.text.lower()
    
    def test_load_complex_pdf(self):
        """Load a second PDF and verify Document structure."""
        loader = PdfLoader()
        doc = loader.load(COMPLEX_PDF)
        
        # Verify Document structure
        assert isinstance(doc, Document)
        assert doc.id.startswith("doc_")
        assert len(doc.text) > 0
        
        # Verify required metadata
        assert doc.metadata["source_path"] == str(COMPLEX_PDF)
        assert doc.metadata["doc_type"] == "pdf"
        assert "doc_hash" in doc.metadata
    
    def test_document_is_serializable(self):
        """Verify loaded Document can be serialized to dict/JSON."""
        loader = PdfLoader()
        doc = loader.load(SIMPLE_PDF)
        
        doc_dict = doc.to_dict()
        assert isinstance(doc_dict, dict)
        assert "id" in doc_dict
        assert "text" in doc_dict
        assert "metadata" in doc_dict
        
        # Verify can recreate from dict
        doc_recreated = Document.from_dict(doc_dict)
        assert doc_recreated.id == doc.id
        assert doc_recreated.text == doc.text
    
    def test_file_hash_consistency(self):
        """Verify same file produces same hash."""
        loader = PdfLoader()
        
        doc1 = loader.load(SIMPLE_PDF)
        doc2 = loader.load(SIMPLE_PDF)
        
        # Same file should produce same doc_hash
        assert doc1.metadata["doc_hash"] == doc2.metadata["doc_hash"]
    
    def test_different_files_different_hash(self):
        """Verify different files produce different hashes."""
        loader = PdfLoader()
        
        doc1 = loader.load(SIMPLE_PDF)
        doc2 = loader.load(COMPLEX_PDF)
        
        # Different files should produce different hashes
        assert doc1.metadata["doc_hash"] != doc2.metadata["doc_hash"]
