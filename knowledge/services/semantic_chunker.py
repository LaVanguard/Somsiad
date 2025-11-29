"""
Semantic chunking for legal documents.
Splits by logical structure (articles, sections) instead of fixed character count.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class LegalChunk:
    """Represents a semantically meaningful chunk of legal text."""

    content: str
    chunk_type: str  # 'article', 'section', 'paragraph', 'preamble'
    article_number: str = None
    section_name: str = None
    paragraph_number: str = None
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dict for storage."""
        return {
            "content": self.content,
            "chunk_type": self.chunk_type,
            "article_number": self.article_number,
            "section_name": self.section_name,
            "paragraph_number": self.paragraph_number,
            "metadata": self.metadata or {},
        }


class SemanticChunker:
    """
    Intelligent chunking for Polish legal documents.

    Chunking strategy:
    1. Split by articles (Art. 1, Art. 2, etc.)
    2. Split by sections (Rozdział, Dział)
    3. Keep paragraphs together
    4. Preserve structure and context
    """

    def __init__(self, max_chunk_size: int = 1500):
        """
        Initialize semantic chunker.

        Args:
            max_chunk_size: Maximum chars per chunk (fallback for very long articles)
        """
        self.max_chunk_size = max_chunk_size

        # Regex patterns for Polish legal documents
        self.patterns = {
            # Articles: Art. 1., Art. 2., etc.
            "article": re.compile(r"Art\.\s*\d+[a-z]?\s*\.", re.IGNORECASE),
            # Sections: Rozdział 1, Rozdział II, DZIAŁ I, etc.
            "section": re.compile(
                r"(DZIAŁ|Rozdział|ROZDZIAŁ)\s+([IVX]+|\d+)\s*[:\n]", re.IGNORECASE
            ),
            # Paragraphs: § 1, § 2
            "paragraph": re.compile(r"§\s*\d+\s*\.?", re.IGNORECASE),
            # Ustęp (subsection): 1., 2., 3.
            "subsection": re.compile(r"^\d+\.\s+", re.MULTILINE),
        }

    def chunk_document(self, text: str, metadata: Dict = None) -> List[LegalChunk]:
        """
        Chunk legal document by semantic structure.

        Args:
            text: Full document text (preprocessed)
            metadata: Document-level metadata

        Returns:
            List of LegalChunk objects
        """
        chunks = []

        # 1. First, split by sections (Rozdział, Dział)
        sections = self._split_by_sections(text)

        for section_name, section_text in sections:
            # 2. Within each section, split by articles
            articles = self._split_by_articles(section_text)

            for article_num, article_text in articles:
                # 3. Check if article is too long
                if len(article_text) > self.max_chunk_size:
                    # Split long articles by paragraphs
                    sub_chunks = self._split_long_article(article_text, article_num)
                    chunks.extend(sub_chunks)
                else:
                    # Keep article as single chunk
                    chunk = LegalChunk(
                        content=article_text.strip(),
                        chunk_type="article",
                        article_number=article_num,
                        section_name=section_name,
                        metadata=metadata,
                    )
                    chunks.append(chunk)

        return chunks

    def _split_by_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Split document by sections (Rozdział, Dział).

        Returns:
            List of (section_name, section_text) tuples
        """
        # Find all section markers
        matches = list(self.patterns["section"].finditer(text))

        if not matches:
            # No sections found - return whole text as one section
            return [("Cały dokument", text)]

        sections = []

        for i, match in enumerate(matches):
            section_name = match.group(0).strip()
            start = match.start()

            # Find end (next section or end of text)
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end]

            sections.append((section_name, section_text))

        # Add preamble if there's text before first section
        if matches[0].start() > 0:
            preamble_text = text[: matches[0].start()]
            if preamble_text.strip():
                sections.insert(0, ("Preambuła", preamble_text))

        return sections

    def _split_by_articles(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by articles (Art. 1, Art. 2, etc.).

        Returns:
            List of (article_number, article_text) tuples
        """
        # Find all article markers
        matches = list(self.patterns["article"].finditer(text))

        if not matches:
            # No articles found - try paragraphs
            return self._split_by_paragraphs(text)

        articles = []

        for i, match in enumerate(matches):
            article_marker = match.group(0)
            # Extract just the number: "Art. 5." → "5"
            article_num = re.search(r"\d+[a-z]?", article_marker).group(0)

            start = match.start()
            # Find end (next article or end of text)
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            article_text = text[start:end]

            articles.append((f"Art. {article_num}", article_text))

        # Add preamble if there's text before first article
        if matches[0].start() > 0:
            preamble_text = text[: matches[0].start()]
            if preamble_text.strip():
                articles.insert(0, ("Przepisy ogólne", preamble_text))

        return articles

    def _split_by_paragraphs(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by paragraphs (§ 1, § 2, etc.).
        Fallback when no articles found.

        Returns:
            List of (paragraph_id, paragraph_text) tuples
        """
        matches = list(self.patterns["paragraph"].finditer(text))

        if not matches:
            # No structure found - return as single chunk
            return [("Fragment", text)]

        paragraphs = []

        for i, match in enumerate(matches):
            para_marker = match.group(0)
            para_num = re.search(r"\d+", para_marker).group(0)

            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            para_text = text[start:end]

            paragraphs.append((f"§ {para_num}", para_text))

        return paragraphs

    def _split_long_article(
        self, article_text: str, article_num: str
    ) -> List[LegalChunk]:
        """
        Split very long articles into smaller chunks.
        Tries to split by subsections (1., 2., 3.)

        Args:
            article_text: Article text
            article_num: Article number (e.g., "Art. 5")

        Returns:
            List of LegalChunk objects
        """
        # Find subsection markers (1., 2., 3.)
        matches = list(self.patterns["subsection"].finditer(article_text))

        if not matches or len(matches) < 2:
            # Can't split meaningfully - chunk by size as fallback
            return self._chunk_by_size(article_text, article_num)

        chunks = []

        for i, match in enumerate(matches):
            subsection_num = match.group(0).strip()
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(article_text)
            subsection_text = article_text[start:end]

            chunk = LegalChunk(
                content=subsection_text.strip(),
                chunk_type="subsection",
                article_number=article_num,
                paragraph_number=subsection_num.rstrip("."),
                metadata={},
            )
            chunks.append(chunk)

        return chunks

    def _chunk_by_size(self, text: str, article_num: str) -> List[LegalChunk]:
        """
        Fallback: chunk by size when semantic splitting fails.

        Args:
            text: Text to chunk
            article_num: Article identifier

        Returns:
            List of LegalChunk objects
        """
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space

            if current_size >= self.max_chunk_size:
                chunk = LegalChunk(
                    content=" ".join(current_chunk),
                    chunk_type="fragment",
                    article_number=article_num,
                    metadata={"split_reason": "size_limit"},
                )
                chunks.append(chunk)
                current_chunk = []
                current_size = 0

        # Add remaining text
        if current_chunk:
            chunk = LegalChunk(
                content=" ".join(current_chunk),
                chunk_type="fragment",
                article_number=article_num,
                metadata={"split_reason": "size_limit"},
            )
            chunks.append(chunk)

        return chunks

    def extract_metadata(self, chunk: LegalChunk) -> Dict:
        """
        Extract rich metadata from chunk.

        Args:
            chunk: LegalChunk object

        Returns:
            Dict with extracted metadata (keywords, references, etc.)
        """
        metadata = chunk.metadata or {}

        # Extract article references (e.g., "art. 5", "Art. 10")
        article_refs = re.findall(r"art\.?\s*\d+[a-z]?", chunk.content, re.IGNORECASE)
        metadata["article_references"] = list(set(article_refs))

        # Extract paragraph references (§)
        para_refs = re.findall(r"§\s*\d+", chunk.content)
        metadata["paragraph_references"] = list(set(para_refs))

        # Extract measurements/distances (common in building law)
        measurements = re.findall(r"\d+[,.]?\d*\s*(?:m|cm|mm|km)", chunk.content)
        metadata["measurements"] = list(set(measurements))

        # Detect if chunk contains obligations/requirements
        obligation_keywords = ["należy", "powinien", "musi", "zobowiązany", "obowiązek"]
        has_obligations = any(kw in chunk.content.lower() for kw in obligation_keywords)
        metadata["contains_obligations"] = has_obligations

        return metadata
