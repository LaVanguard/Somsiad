"""
Document summarization service for generating hierarchical summaries.
Creates document-level and section-level summaries for better RAG context.
"""

import logging
from typing import Dict, List

from django.conf import settings
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class DocumentSummarizer:
    """
    Generate summaries at multiple levels for hierarchical RAG.

    Levels:
    1. Document-level: Executive summary of entire law
    2. Section-level: Summary of each major section
    3. Chunk-level: Brief context for each chunk
    """

    def __init__(self):
        """Initialize summarizer with LLM."""
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.2,  # Lower for more consistent summaries
        )

    def generate_document_summary(
        self, full_text: str, document_title: str, max_length: int = 500
    ) -> Dict[str, str]:
        """
        Generate executive summary of entire document.

        Args:
            full_text: Full document text
            document_title: Document title
            max_length: Maximum summary length in words

        Returns:
            Dict with 'summary' and 'key_topics'
        """
        # Truncate if text is very long (to fit in context window)
        text_preview = full_text[:8000] if len(full_text) > 8000 else full_text

        prompt = f"""Jesteś ekspertem prawnym specjalizującym się w polskim prawie budowlanym.

Przeanalizuj poniższy dokument prawny i stwórz:

1. STRESZCZENIE (3-5 zdań): Zwięzłe podsumowanie głównych przepisów
2. KLUCZOWE TEMATY: 5-7 najważniejszych tematów poruszonych w dokumencie
3. ZAKRES ZASTOSOWANIA: Kogo i co dotyczy ten dokument

Dokument: {document_title}

Tekst:
{text_preview}

Format odpowiedzi:
STRESZCZENIE:
[twoje streszczenie]

KLUCZOWE TEMATY:
- [temat 1]
- [temat 2]
...

ZAKRES ZASTOSOWANIA:
[opis zakresu]
"""

        try:
            response = self.llm.invoke(prompt)
            summary_text = response.content

            # Parse response
            summary = self._parse_summary_response(summary_text)

            logger.info(f"Generated document summary for {document_title}")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {
                "summary": f"Dokument: {document_title}",
                "key_topics": [],
                "scope": "Nie udało się wygenerować podsumowania",
            }

    def generate_section_summaries(self, sections: List[tuple]) -> Dict[str, str]:
        """
        Generate summaries for each major section.

        Args:
            sections: List of (section_name, section_text) tuples

        Returns:
            Dict mapping section_name → summary
        """
        summaries = {}

        for section_name, section_text in sections:
            if len(section_text.strip()) < 100:
                # Skip very short sections
                continue

            # Truncate long sections
            text_preview = (
                section_text[:3000] if len(section_text) > 3000 else section_text
            )

            prompt = f"""Stwórz zwięzłe podsumowanie (2-3 zdania) tej sekcji dokumentu prawnego:

Sekcja: {section_name}

Tekst:
{text_preview}

Podsumowanie (2-3 zdania):"""

            try:
                response = self.llm.invoke(prompt)
                summary = response.content.strip()
                summaries[section_name] = summary
                logger.info(f"Generated summary for section: {section_name}")

            except Exception as e:
                logger.error(f"Failed to generate summary for {section_name}: {e}")
                summaries[section_name] = f"Sekcja {section_name}"

        return summaries

    def generate_chunk_context(
        self, chunk_text: str, article_number: str = None, section_name: str = None
    ) -> str:
        """
        Generate brief context/title for a chunk.

        Args:
            chunk_text: Chunk text
            article_number: Article number (e.g., "Art. 5")
            section_name: Section name

        Returns:
            Brief context string (1 sentence)
        """
        # For short chunks, use article number as context
        if article_number and len(chunk_text) < 500:
            return f"{article_number} - przepisy dotyczące..."

        # Truncate long chunks
        text_preview = chunk_text[:800] if len(chunk_text) > 800 else chunk_text

        prompt = f"""Stwórz krótki tytuł/kontekst (1 krótkie zdanie) dla tego fragmentu prawa:

Fragment:
{text_preview}

Tytuł (1 zdanie):"""

        try:
            response = self.llm.invoke(prompt)
            context = response.content.strip()
            return context

        except Exception as e:
            logger.error(f"Failed to generate chunk context: {e}")
            return f"{article_number or 'Fragment'} - przepisy prawne"

    def extract_key_obligations(self, text: str) -> List[str]:
        """
        Extract key obligations/requirements from legal text.

        Args:
            text: Legal text

        Returns:
            List of key obligations (max 5)
        """
        prompt = f"""Wypisz 3-5 najważniejszych obowiązków lub wymagań z tego tekstu prawnego.
Każdy obowiązek w jednej linii zaczynając od "-".

Tekst:
{text[:2000]}

Obowiązki:"""

        try:
            response = self.llm.invoke(prompt)
            obligations_text = response.content.strip()

            # Parse bullet points
            obligations = [
                line.strip().lstrip("-").strip()
                for line in obligations_text.split("\n")
                if line.strip().startswith("-")
            ]

            return obligations[:5]  # Max 5

        except Exception as e:
            logger.error(f"Failed to extract obligations: {e}")
            return []

    def _parse_summary_response(self, response: str) -> Dict[str, any]:
        """
        Parse structured summary response.

        Args:
            response: LLM response text

        Returns:
            Dict with parsed fields
        """
        result = {"summary": "", "key_topics": [], "scope": ""}

        # Extract sections
        sections = {
            "STRESZCZENIE:": "summary",
            "KLUCZOWE TEMATY:": "key_topics",
            "ZAKRES ZASTOSOWANIA:": "scope",
        }

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()

            # Check if line is a section header
            for header, field in sections.items():
                if header in line:
                    current_section = field
                    break

            # Add content to current section
            if current_section and line and not any(h in line for h in sections.keys()):
                if current_section == "key_topics":
                    # Parse bullet points
                    if line.startswith("-") or line.startswith("•"):
                        topic = line.lstrip("-•").strip()
                        result["key_topics"].append(topic)
                elif current_section == "summary":
                    result["summary"] += line + " "
                elif current_section == "scope":
                    result["scope"] += line + " "

        # Clean up
        result["summary"] = result["summary"].strip()
        result["scope"] = result["scope"].strip()

        return result

    def create_searchable_summary_chunk(
        self, document_id: int, document_title: str, summary: Dict
    ) -> Dict:
        """
        Create a searchable summary chunk for the document.
        This gets embedded and stored alongside regular chunks.

        Args:
            document_id: Document ID
            document_title: Document title
            summary: Summary dict from generate_document_summary()

        Returns:
            Formatted chunk for embedding
        """
        # Combine summary fields into searchable text
        summary_text = f"""DOKUMENT: {document_title}

STRESZCZENIE:
{summary['summary']}

KLUCZOWE TEMATY:
{chr(10).join(f"- {topic}" for topic in summary['key_topics'])}

ZAKRES ZASTOSOWANIA:
{summary['scope']}
"""

        return {
            "content": summary_text,
            "metadata": {
                "document_id": document_id,
                "document_title": document_title,
                "chunk_type": "document_summary",
                "is_summary": True,
                **summary,
            },
        }
