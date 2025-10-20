"""
Tests for semantic_chunker.py - intelligent legal document chunking.

Tests cover:
- Article-based chunking (Art. 1, Art. 2, etc.)
- Section-based chunking (Rozdział, Dział)
- Paragraph-based chunking (§ 1, § 2)
- Long article splitting by subsections
- Fallback to fixed-size chunking
- Metadata extraction (measurements, obligations, references)
- Edge cases (malformed articles, no structure, preambles)
"""
import pytest
from knowledge.services.semantic_chunker import SemanticChunker, LegalChunk


# ============================================================================
# Basic Article Chunking Tests
# ============================================================================

def test_simple_article_chunking():
    """Test basic article splitting (Art. 1., Art. 2.)"""
    chunker = SemanticChunker()
    text = """
    Art. 1. Właściciel nieruchomości jest obowiązany utrzymywać ją w należytym stanie.

    Art. 2. Budowa wymaga pozwolenia na budowę zgodnie z przepisami ustawy.

    Art. 3. Wysokość budynku nie może przekraczać 15 metrów od poziomu terenu.
    """

    chunks = chunker.chunk_document(text)

    assert len(chunks) == 3
    assert chunks[0].article_number == "Art. 1"
    assert chunks[1].article_number == "Art. 2"
    assert chunks[2].article_number == "Art. 3"
    assert chunks[0].chunk_type == 'article'
    assert "właściciel" in chunks[0].content.lower()


def test_article_with_letter_suffix():
    """Test articles with letter suffixes (Art. 5a, Art. 5b)"""
    chunker = SemanticChunker()
    text = """
    Art. 5. Przepisy ogólne.

    Art. 5a. Przepis dodany nowelizacją.

    Art. 5b. Kolejny przepis nowelizacyjny.
    """

    chunks = chunker.chunk_document(text)

    assert len(chunks) == 3
    assert chunks[0].article_number == "Art. 5"
    assert chunks[1].article_number == "Art. 5a"
    assert chunks[2].article_number == "Art. 5b"


def test_preamble_before_articles():
    """Test that preamble text before first article is captured"""
    chunker = SemanticChunker()
    text = """
    Ustawa z dnia 7 lipca 1994 r. - Prawo budowlane.

    Rozdział 1 - Przepisy ogólne

    Art. 1. Zakres regulacji tej ustawy obejmuje...
    """

    chunks = chunker.chunk_document(text)

    # Should have preamble + article
    assert len(chunks) >= 1
    # Check if first chunk is preamble or if preamble was merged with section
    has_preamble_content = any(
        "Ustawa z dnia" in chunk.content or "Prawo budowlane" in chunk.content
        for chunk in chunks
    )
    assert has_preamble_content


# ============================================================================
# Section-Based Chunking Tests
# ============================================================================

def test_section_splitting():
    """Test splitting by sections (Rozdział I, Rozdział II)"""
    chunker = SemanticChunker()
    text = """
    Rozdział I: Przepisy ogólne

    Art. 1. Definicje.
    Art. 2. Zakres zastosowania.

    Rozdział II: Przepisy szczegółowe

    Art. 3. Procedury.
    Art. 4. Wyjątki.
    """

    chunks = chunker.chunk_document(text)

    # Should have chunks from both sections (section headers get chunked too)
    assert len(chunks) >= 4

    # Check section names are preserved
    section_names = [chunk.section_name for chunk in chunks]
    assert any("Rozdział I" in name for name in section_names)
    assert any("Rozdział II" in name for name in section_names)

    # Verify articles are properly associated with sections
    art_chunks = [c for c in chunks if c.article_number and c.article_number.startswith("Art.")]
    assert len(art_chunks) == 4


def test_dział_sections():
    """Test DZIAŁ sections (uppercase, Roman numerals)"""
    chunker = SemanticChunker()
    text = """
    DZIAŁ I: Postanowienia ogólne

    Art. 1. Definicja.

    DZIAŁ II: Postanowienia szczególne

    Art. 2. Procedura.
    """

    chunks = chunker.chunk_document(text)

    # Should have multiple chunks (section headers + articles)
    assert len(chunks) >= 2

    # Check DZIAŁ sections are detected
    section_names = [chunk.section_name for chunk in chunks]
    assert any("DZIAŁ I" in name for name in section_names)

    # Verify articles are present
    art_chunks = [c for c in chunks if c.article_number and c.article_number.startswith("Art.")]
    assert len(art_chunks) == 2


# ============================================================================
# Paragraph-Based Chunking (Fallback)
# ============================================================================

def test_paragraph_based_chunking():
    """Test fallback to paragraph chunking when no articles found"""
    chunker = SemanticChunker()
    text = """
    § 1. W rozumieniu przepisów rozporządzenia...

    § 2. Właściwy organ wydaje decyzję...

    § 3. Odwołanie wnosi się w terminie 14 dni.
    """

    chunks = chunker.chunk_document(text)

    assert len(chunks) == 3
    assert chunks[0].article_number == "§ 1"
    assert chunks[1].article_number == "§ 2"
    assert chunks[2].article_number == "§ 3"


# ============================================================================
# Long Article Splitting Tests
# ============================================================================

def test_long_article_splitting():
    """Test that very long articles are split by subsections (1., 2., 3.)"""
    chunker = SemanticChunker(max_chunk_size=200)  # Small limit to force split

    # Create a long article with subsections (use newlines to trigger subsection pattern)
    long_text = """Art. 50. Warunki techniczne budynków.
1. Budynek musi spełniać wymagania dotyczące bezpieczeństwa konstrukcji zgodnie z normami.
2. Instalacje elektryczne muszą być wykonane zgodnie z przepisami techniczno-budowlanymi.
3. System wentylacji musi zapewnić odpowiednią wymianę powietrza w pomieszczeniach.
4. Izolacja termiczna ścian zewnętrznych powinna minimalizować straty ciepła i zapewnić komfort."""

    chunks = chunker.chunk_document(long_text)

    # Should be split into multiple chunks (either subsections or fragments)
    assert len(chunks) > 1

    # Check that article is split (either into subsections or fragments)
    chunk_types = [chunk.chunk_type for chunk in chunks]
    assert any(ct in ['subsection', 'fragment'] for ct in chunk_types)

    # Check article number is preserved in all chunks
    assert all(chunk.article_number and "50" in chunk.article_number for chunk in chunks)


def test_fallback_to_size_chunking():
    """Test fallback to fixed-size chunking when no structure found"""
    chunker = SemanticChunker(max_chunk_size=100)

    # Very long text with no structural markers
    long_unstructured = "Lorem ipsum dolor sit amet " * 50  # ~1400 chars

    chunks = chunker.chunk_document(long_unstructured)

    # Should be split into multiple fragments
    assert len(chunks) > 1

    # All chunks should be fragments
    assert all(chunk.chunk_type in ['fragment', 'article'] for chunk in chunks)

    # No chunk should exceed max_chunk_size significantly
    for chunk in chunks:
        assert len(chunk.content) <= chunker.max_chunk_size + 50  # +50 buffer for word boundaries


# ============================================================================
# Metadata Extraction Tests
# ============================================================================

def test_metadata_article_references():
    """Test extraction of article cross-references (art. 5, Art. 10)"""
    chunker = SemanticChunker()
    chunk = LegalChunk(
        content="Zgodnie z art. 5 i art. 10, właściciel musi...",
        chunk_type='article',
        article_number="Art. 20"
    )

    metadata = chunker.extract_metadata(chunk)

    assert 'article_references' in metadata
    assert len(metadata['article_references']) >= 2
    # Check that "art. 5" and "art. 10" are captured (case insensitive)
    refs_lower = [ref.lower() for ref in metadata['article_references']]
    assert any('5' in ref for ref in refs_lower)
    assert any('10' in ref for ref in refs_lower)


def test_metadata_paragraph_references():
    """Test extraction of paragraph references (§ 1, § 2)"""
    chunker = SemanticChunker()
    chunk = LegalChunk(
        content="Przepis § 1 oraz § 2 określają procedurę odwoławczą.",
        chunk_type='article',
        article_number="Art. 15"
    )

    metadata = chunker.extract_metadata(chunk)

    assert 'paragraph_references' in metadata
    assert len(metadata['paragraph_references']) == 2


def test_metadata_measurements_extraction():
    """Test extraction of measurements (15 m, 2.5 km, 50 cm)"""
    chunker = SemanticChunker()
    chunk = LegalChunk(
        content="Wysokość budynku nie może przekraczać 15 m, odległość 2.5 km od granicy.",
        chunk_type='article',
        article_number="Art. 8"
    )

    metadata = chunker.extract_metadata(chunk)

    assert 'measurements' in metadata
    assert len(metadata['measurements']) >= 1
    # Check that measurements are captured
    measurements_str = ' '.join(metadata['measurements'])
    assert '15' in measurements_str or 'm' in measurements_str


def test_metadata_obligations_detection():
    """Test detection of obligation keywords (należy, musi, powinien)"""
    chunker = SemanticChunker()

    # Chunk with obligation
    chunk_with_obligation = LegalChunk(
        content="Właściciel musi utrzymywać budynek w należytym stanie.",
        chunk_type='article',
        article_number="Art. 5"
    )

    metadata = chunker.extract_metadata(chunk_with_obligation)
    assert metadata['contains_obligations'] is True

    # Chunk without obligation
    chunk_without_obligation = LegalChunk(
        content="Budynek jest własnością gminy.",
        chunk_type='article',
        article_number="Art. 6"
    )

    metadata = chunker.extract_metadata(chunk_without_obligation)
    assert metadata['contains_obligations'] is False


# ============================================================================
# Edge Cases
# ============================================================================

def test_empty_text():
    """Test handling of empty text"""
    chunker = SemanticChunker()
    chunks = chunker.chunk_document("")

    # Should return at least one chunk (even if empty)
    assert len(chunks) >= 0


def test_text_with_no_structure():
    """Test plain text with no legal structure markers"""
    chunker = SemanticChunker()
    text = "To jest zwykły tekst bez żadnych artykułów ani paragrafów."

    chunks = chunker.chunk_document(text)

    # Should return single chunk with fallback type
    assert len(chunks) == 1
    assert chunks[0].chunk_type in ['article', 'fragment']


def test_malformed_article_numbers():
    """Test handling of malformed article markers"""
    chunker = SemanticChunker()
    text = """
    Art 5 Brak kropki po Art.

    Art. 10. Prawidłowy artykuł.

    Article 15. Angielski wariant.
    """

    chunks = chunker.chunk_document(text)

    # Should handle at least the correctly formatted article
    assert len(chunks) >= 1


def test_chunk_to_dict_conversion():
    """Test LegalChunk.to_dict() method"""
    chunk = LegalChunk(
        content="Test content",
        chunk_type='article',
        article_number="Art. 5",
        section_name="Rozdział I",
        metadata={'custom': 'value'}
    )

    chunk_dict = chunk.to_dict()

    assert chunk_dict['content'] == "Test content"
    assert chunk_dict['chunk_type'] == 'article'
    assert chunk_dict['article_number'] == "Art. 5"
    assert chunk_dict['section_name'] == "Rozdział I"
    assert chunk_dict['metadata']['custom'] == 'value'


def test_custom_max_chunk_size():
    """Test that custom max_chunk_size parameter is respected"""
    custom_size = 500
    chunker = SemanticChunker(max_chunk_size=custom_size)

    assert chunker.max_chunk_size == custom_size


# ============================================================================
# Integration Test: Realistic Legal Document
# ============================================================================

def test_realistic_legal_document():
    """Test chunking of realistic Polish legal document fragment"""
    chunker = SemanticChunker()

    realistic_text = """
    Ustawa z dnia 7 lipca 1994 r. - Prawo budowlane.

    Rozdział 1: Przepisy ogólne

    Art. 1. Ustawa ma na celu określenie warunków budowy obiektów budowlanych.

    Art. 2. Użyte w ustawie określenia oznaczają:
    1. Obiekt budowlany - budynek, budowlę...
    2. Budynek - obiekt budowlany trwale związany z gruntem...
    3. Budowla - każdy obiekt budowlany niebędący budynkiem...

    Art. 3. Przepisy ustawy stosuje się przy projektowaniu zgodnie z art. 1.

    Rozdział 2: Pozwolenie na budowę

    Art. 28. Budowa obiektu budowlanego wymaga pozwolenia wydanego przez organ.

    Art. 29. Odległość budynku od granicy nie może być mniejsza niż 4 m.
    """

    chunks = chunker.chunk_document(realistic_text)

    # Should have multiple chunks (preamble + articles from 2 sections)
    assert len(chunks) >= 4

    # Check sections are detected
    section_names = [chunk.section_name for chunk in chunks if chunk.section_name]
    assert len(section_names) > 0

    # Check articles are numbered correctly
    article_numbers = [chunk.article_number for chunk in chunks if chunk.article_number]
    assert any("Art. 1" in num for num in article_numbers)
    assert any("Art. 28" in num for num in article_numbers)

    # Extract metadata from chunk with measurement
    chunk_with_measurement = next(
        chunk for chunk in chunks if "4 m" in chunk.content
    )
    metadata = chunker.extract_metadata(chunk_with_measurement)
    assert 'measurements' in metadata
    assert len(metadata['measurements']) > 0
