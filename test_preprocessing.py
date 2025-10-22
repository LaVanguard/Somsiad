"""
Quick test script to verify document preprocessing.
Tests with the actual legal PDFs we have.

NOTE: This test requires actual PDF files in legal_documents/ directory.
Skip in CI/CD environments where files are not available.
"""
import sys
import os
import pytest

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from PyPDF2 import PdfReader
from knowledge.services.preprocessor import DocumentPreprocessor


@pytest.mark.skip(reason="Requires PDF files in legal_documents/ (not in git)")
def test_preprocessing():
    """Test preprocessing on a sample legal PDF."""

    # Test file
    pdf_path = "legal_documents/raw/budowa/warunki_techniczne_metro_2023.pdf"

    print("=" * 80)
    print("PREPROCESSING TEST")
    print("=" * 80)
    print(f"\nTest file: {pdf_path}")

    # Extract first page
    reader = PdfReader(pdf_path)
    first_page = reader.pages[0].extract_text()

    print(f"\nTotal pages in PDF: {len(reader.pages)}")
    print(f"\nFirst page length: {len(first_page)} characters")

    # Show raw text preview
    print("\n" + "-" * 80)
    print("RAW TEXT (first 500 chars):")
    print("-" * 80)
    print(first_page[:500])

    # Preprocess
    preprocessor = DocumentPreprocessor()
    result = preprocessor.preprocess(first_page)

    cleaned = result['cleaned']

    # Show cleaned text preview
    print("\n" + "-" * 80)
    print("CLEANED TEXT (first 500 chars):")
    print("-" * 80)
    print(cleaned[:500])

    # Show statistics
    stats = preprocessor.get_stats(first_page, cleaned)

    print("\n" + "=" * 80)
    print("PREPROCESSING STATISTICS")
    print("=" * 80)
    print(f"Characters before:  {stats['chars_before']:,}")
    print(f"Characters after:   {stats['chars_after']:,}")
    print(f"Characters removed: {stats['chars_removed']:,}")
    print(f"Reduction:          {stats['reduction_pct']}%")
    print(f"Words before:       {stats['words_before']:,}")
    print(f"Words after:        {stats['words_after']:,}")

    # Test encoding fixes
    print("\n" + "=" * 80)
    print("ENCODING FIXES TEST")
    print("=" * 80)

    # Check for common encoding issues
    encoding_issues = {
        '�': first_page.count('�'),
        '\u0142': first_page.count('\u0142'),
    }

    print("\nEncoding issues found in raw text:")
    for char, count in encoding_issues.items():
        if count > 0:
            print(f"  '{char}' appears {count} times")

    print("\nPreprocessing test complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_preprocessing()
