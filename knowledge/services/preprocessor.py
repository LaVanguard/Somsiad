"""
Document preprocessing service for cleaning legal documents.
Removes administrative metadata and formatting noise from Polish legal PDFs.
"""
import re
from typing import Dict


class DocumentPreprocessor:
    """
    Clean and preprocess legal documents before RAG processing.

    Removes common noise from Polish legal documents:
    - Administrative headers (Kancelaria Sejmu, Dziennik Ustaw)
    - Page numbers and metadata
    - Dates and signatures
    - Encoding artifacts
    """

    def __init__(self):
        """Initialize preprocessor with cleaning patterns."""
        self.encoding_fixes = {
            '�': 'ł',
            '\u0142': 'ł',
            '¹': 'ą',
            '�': 'ę',
            '³': 'ł',
            'ñ': 'ń',
            'œ': 'ś',
            'Ÿ': 'ź',
            '¿': 'ż',
        }

    def clean_polish_legal_document(self, text: str) -> str:
        """
        Remove common noise from Polish legal PDFs.

        Args:
            text: Raw PDF text

        Returns:
            Cleaned text ready for chunking
        """
        # 1. Remove Sejm/Parliament headers
        text = re.sub(r'Kancelaria Sejmu\s+s\.\s*\d+/\d+', '', text, flags=re.IGNORECASE)

        # 2. Remove Journal (Dziennik Ustaw) references
        text = re.sub(r'Dz\.\s*U\..*?poz\.\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'DZIENNIK\s+USTAW.*?Poz\.\s*\d+', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'RZECZYPOSPOLITEJ\s+POLSKIEJ', '', text, flags=re.IGNORECASE)

        # 3. Remove ministry headers and regulations metadata
        text = re.sub(r'ROZPORZ[ĄĄ]DZENIE\s+MINISTRA.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'OBWIESZCZENIE\s+MINISTRA.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'USTAWA\s+z\s+dnia\s+\d+.*?\d{4}\s*r\.', '', text, flags=re.IGNORECASE)

        # 4. Remove dates and locations
        text = re.sub(r'Warszawa,\s*dnia\s+\d+.*?\d{4}\s*r\.', '', text, flags=re.IGNORECASE)

        # 5. Remove signatures and official closings
        text = re.sub(r'Minister\s+\w+.*?podpis', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Prezes\s+Rady\s+Ministrów.*', '', text, flags=re.IGNORECASE)

        # 6. Remove page markers
        text = re.sub(r'Strona\s+\d+\s+z\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'–\s*\d+\s*–', '', text)

        # 7. Remove amendment markers (optional - may want to keep)
        text = re.sub(r'\(uchylony\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(zmieniony\)', '', text, flags=re.IGNORECASE)

        # 8. Fix common encoding issues
        for bad_char, good_char in self.encoding_fixes.items():
            text = text.replace(bad_char, good_char)

        # 9. Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r' {2,}', ' ', text)      # Max 1 space
        text = re.sub(r'\t+', ' ', text)        # Tabs to space

        # 10. Remove leading/trailing whitespace
        text = text.strip()

        return text

    def extract_substantive_articles(self, text: str) -> str:
        """
        Extract only substantive articles from legal text.
        Filters out administrative provisions.

        Args:
            text: Cleaned legal text

        Returns:
            Text with only substantive legal provisions
        """
        # Split into article blocks
        # Pattern: Art. 1, Art. 2, etc.
        articles = re.split(r'(Art\.\s*\d+\.)', text)

        # Reconstruct with articles
        substantive_blocks = []
        for i in range(1, len(articles), 2):
            article_number = articles[i]
            article_text = articles[i+1] if i+1 < len(articles) else ''

            # Skip administrative articles
            skip_patterns = [
                'traci moc',
                'wchodzi w życie',
                'rozporządzenie podlega',
                'ogłasza się',
                'minister właściwy',
            ]

            if not any(pattern in article_text.lower() for pattern in skip_patterns):
                substantive_blocks.append(article_number + article_text)

        return '\n\n'.join(substantive_blocks)

    def preprocess(
        self,
        text: str,
        extract_substantive: bool = False
    ) -> Dict[str, str]:
        """
        Full preprocessing pipeline.

        Args:
            text: Raw PDF text
            extract_substantive: If True, filter to only substantive articles

        Returns:
            Dict with 'raw', 'cleaned', and optionally 'substantive' text
        """
        result = {
            'raw': text,
            'cleaned': self.clean_polish_legal_document(text)
        }

        if extract_substantive:
            result['substantive'] = self.extract_substantive_articles(result['cleaned'])

        return result

    def get_stats(self, before: str, after: str) -> Dict:
        """
        Calculate preprocessing statistics.

        Args:
            before: Text before preprocessing
            after: Text after preprocessing

        Returns:
            Dict with character/word count changes
        """
        return {
            'chars_removed': len(before) - len(after),
            'chars_before': len(before),
            'chars_after': len(after),
            'reduction_pct': round((1 - len(after)/len(before)) * 100, 2) if len(before) > 0 else 0,
            'words_before': len(before.split()),
            'words_after': len(after.split()),
        }
