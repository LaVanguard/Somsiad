"""
Memetic Actions Service
Generates fake legal actions (Prosecutor, Donos, Municipal Guard) using GPT-5 mini.
Sprint 9 - Entertainment feature with educational value.
"""

import logging
from typing import Dict, List

from django.conf import settings
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class MemeticActionsService:
    """
    Service for generating memetic (fake but realistic) legal action content.

    All actions are FAKE - they generate realistic content but never send anything.
    Always includes clear disclaimer: "To był żart 😄"
    """

    def __init__(self):
        """Initialize with GPT-5 mini for content generation."""
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.2,  # Low for formal, consistent tone
        )

    def generate_prosecutor_letter(
        self, question: str, ai_answer: str
    ) -> Dict[str, str]:
        """
        Generate formal letter to prosecutor office (zawiadomienie o przestępstwie).

        Args:
            question: User's original question
            ai_answer: AI's legal analysis (for context)

        Returns:
            Dict with 'letter' (str) and 'timestamp' (str)
        """
        prompt = f"""Wygeneruj FORMALNE PISMO do Prokuratury Rejonowej zawiadamiające o popełnieniu przestępstwa.

Kontekst sprawy (pytanie użytkownika): {question}

Analiza prawna AI (dla kontekstu): {ai_answer[:500]}

Wymagania pisma:
1. Nagłówek: "Do Prokuratury Rejonowej w [Miasto - wybierz warszawę/kraków/wrocław losowo]"
2. Data: dzisiejsza (format: Warszawa, dnia [dzień] [miesiąc] 2025 r.)
3. Dane nadawcy (placeholder):
   "Jan Kowalski
   ul. Kwiatowa 15/7
   00-001 Warszawa"
4. Tytuł (wyśrodkowany, bold): "ZAWIADOMIENIE O POPEŁNIENIU PRZESTĘPSTWA"
5. Treść:
   - Krótkie wprowadzenie: "Niniejszym zawiadamiam Prokuraturę o..."
   - Zwięzły opis sytuacji (3-4 zdania, rzeczowo, bez emocji)
   - Wskazanie przepisów które MOGŁY zostać naruszone (konkretne artykuły ustaw)
   - Prośba o wszczęcie postępowania przygotowawczego
6. Informacja o podstawie prawnej: "Zawiadomienie składam na podstawie art. 304 § 2 Kodeksu postępowania karnego"
7. Podpis:
   "Z poważaniem,
   [podpis]
   Jan Kowalski"

Format:
- Profesjonalny, rzeczowy język urzędowy
- Bez emocji i oskarżeń - tylko fakty
- Konkretne wskazanie przepisów (np. "art. 124 ustawy Prawo budowlane")
- Bez żadnych humorystycznych elementów (to dodamy w UI)

Wygeneruj TYLKO tekst pisma, bez dodatkowych komentarzy."""

        try:
            response = self.llm.invoke(prompt)
            letter = response.content.strip()

            logger.info(f"Generated prosecutor letter ({len(letter)} chars)")

            return {"letter": letter, "generated_by": "gpt-5-mini"}

        except Exception as e:
            logger.error(f"Failed to generate prosecutor letter: {e}")
            # Fallback to template
            return {
                "letter": self._get_fallback_prosecutor_letter(question),
                "generated_by": "template",
            }

    def generate_donos_email(self, question: str, ai_answer: str) -> Dict[str, str]:
        """
        Generate anonymous complaint email to municipal office (donos).

        Args:
            question: User's original question
            ai_answer: AI's legal analysis

        Returns:
            Dict with 'subject', 'body', and 'timestamp'
        """
        prompt = f"""Wygeneruj ANONIMOWY EMAIL-DONOS do Rady Gminy/Urzędu Miasta.

Kontekst sprawy: {question}

Analiza prawna AI: {ai_answer[:500]}

Wymagania emaila:

TEMAT (krótki, konkretny):
"Zgłoszenie nieprawidłowości - [zwięzły opis max 8 słów]"

TREŚĆ:
1. Otwarcie: "Szanowni Państwo,"
2. Wprowadzenie (1 zdanie): "Zwracam się z prośbą o interwencję w następującej sprawie:"
3. Opis problemu (2-3 zdania):
   - Konkretny opis sytuacji
   - Wskazanie lokalizacji (fikcyjna ale realistyczna: np. "ul. Polna 15")
   - Bez emocji, rzeczowo
4. Wskazanie przepisów (1-2 zdania):
   - Które przepisy mogą być naruszone
   - Konkretne artykuły ustaw/rozporządzeń
5. Prośba o interwencję (1 zdanie):
   "Proszę o dyskretną interwencję oraz sprawdzenie opisanej sytuacji."
6. Załączniki (1 zdanie):
   "W załączeniu przesyłam dokumentację fotograficzną/dźwiękową problemu."
7. Zakończenie:
   "Z poważaniem,
   Zatroskany Mieszkaniec"
8. Stopka:
   "---
   Email wysłany z adresu anonimowego"

Ton: Grzeczny, oficjalny ale nie przesadnie formalny. Bez agresji, bez oskarżeń - tylko opis faktów.

Wygeneruj TYLKO temat i treść emaila (osobno), bez dodatkowych komentarzy."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Parse subject and body
            if "TEMAT:" in content and "TREŚĆ:" in content:
                parts = content.split("TREŚĆ:")
                subject = parts[0].replace("TEMAT:", "").strip()
                body = parts[1].strip()
            else:
                # Fallback parsing
                lines = content.split("\n", 1)
                subject = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else content

            logger.info(f"Generated donos email (subject: {subject[:50]}...)")

            return {"subject": subject, "body": body, "generated_by": "gpt-5-mini"}

        except Exception as e:
            logger.error(f"Failed to generate donos email: {e}")
            return {
                "subject": "Zgłoszenie nieprawidłowości",
                "body": self._get_fallback_donos_email(question),
                "generated_by": "template",
            }

    def generate_straz_call_script(
        self, question: str, ai_answer: str
    ) -> Dict[str, any]:
        """
        Generate fake phone call script for Municipal Guard (Straż Miejska).

        Args:
            question: User's original question
            ai_answer: AI's legal analysis

        Returns:
            Dict with 'messages' (list of conversation), 'patrol_time' (str)
        """
        prompt = f"""Wygeneruj SCENARIUSZ ROZMOWY TELEFONICZNEJ ze Strażą Miejską.

Kontekst zgłoszenia: {question}

Analiza prawna: {ai_answer[:500]}

Wymagania scenariusza:

Rozmowa składa się z 6-8 wiadomości (naprzemiennie operator i user).

Format każdej wiadomości:
OPERATOR: [tekst]
USER: [tekst]

Scenariusz:
1. OPERATOR: Oficjalne powitanie "Straż Miejska, dyżurny [imię], słucham. W czym mogę pomóc?"
2. USER: Grzeczne zgłoszenie problemu (1-2 zdania, bez histerii)
3. OPERATOR: Pytanie uzupełniające o szczegóły (adres, co dokładnie)
4. USER: Podanie szczegółów (fikcyjna ale realistyczna lokalizacja: np. "ul. Kwiatowa róg Polnej")
5. OPERATOR: Potwierdzenie zrozumienia + informacja "Rozumiem sytuację. Wysyłam patrol do sprawdzenia."
6. USER: Pytanie o czas przyjazdu
7. OPERATOR: "Patrol będzie na miejscu za około 10-15 minut. Czy mogę jeszcze w czymś pomóc?"
8. USER: "Nie, dziękuję za pomoc."
9. OPERATOR: "Do widzenia. W razie czego proszę dzwonić ponownie."

Ton rozmowy:
- OPERATOR: Profesjonalny, rzeczowy, pomocny
- USER: Grzeczny, konkretny, spokojny

Format odpowiedzi:
Zwróć TYLKO listę wiadomości w formacie:
OPERATOR: [tekst]
USER: [tekst]
...

Bez dodatkowych komentarzy."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Parse messages
            messages = []
            msg_id = 1
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("OPERATOR:"):
                    messages.append(
                        {
                            "id": msg_id,
                            "sender": "operator",
                            "text": line.replace("OPERATOR:", "").strip(),
                        }
                    )
                    msg_id += 1
                elif line.startswith("USER:"):
                    messages.append(
                        {
                            "id": msg_id,
                            "sender": "user",
                            "text": line.replace("USER:", "").strip(),
                        }
                    )
                    msg_id += 1

            logger.info(f"Generated Straż call script ({len(messages)} messages)")

            return {
                "messages": messages,
                "patrol_time": "10-15 minut",
                "generated_by": "gpt-5-mini",
            }

        except Exception as e:
            logger.error(f"Failed to generate Straż call script: {e}")
            return {
                "messages": self._get_fallback_straz_script(question),
                "patrol_time": "15 minut",
                "generated_by": "template",
            }

    # Fallback templates (in case GPT fails)

    def _get_fallback_prosecutor_letter(self, question: str) -> str:
        """Fallback template for prosecutor letter."""
        return f"""Do Prokuratury Rejonowej w Warszawie

Warszawa, dnia {self._get_current_date()}

Jan Kowalski
ul. Kwiatowa 15/7
00-001 Warszawa

ZAWIADOMIENIE O POPEŁNIENIU PRZESTĘPSTWA

Niniejszym zawiadamiam Prokuraturę o możliwości popełnienia przestępstwa.

Sprawa dotyczy: {question[:200]}

Proszę o wszczęcie postępowania przygotowawczego w tej sprawie oraz podjęcie stosownych czynności.

Zawiadomienie składam na podstawie art. 304 § 2 Kodeksu postępowania karnego.

Z poważaniem,
[podpis]
Jan Kowalski"""

    def _get_fallback_donos_email(self, question: str) -> str:
        """Fallback template for donos email."""
        return f"""Szanowni Państwo,

Zwracam się z prośbą o interwencję w następującej sprawie: {question[:150]}

Proszę o dyskretną interwencję oraz sprawdzenie opisanej sytuacji.

W załączeniu przesyłam dokumentację fotograficzną problemu.

Z poważaniem,
Zatroskany Mieszkaniec

---
Email wysłany z adresu anonimowego"""

    def _get_fallback_straz_script(self, question: str) -> List[Dict]:
        """Fallback template for Straż call."""
        return [
            {
                "id": 1,
                "sender": "operator",
                "text": "Straż Miejska, dyżurny Kowalski, słucham. W czym mogę pomóc?",
            },
            {
                "id": 2,
                "sender": "user",
                "text": f"Dzień dobry, zgłaszam problem: {question[:100]}",
            },
            {
                "id": 3,
                "sender": "operator",
                "text": "Rozumiem. Wysyłam patrol do sprawdzenia sytuacji.",
            },
            {
                "id": 4,
                "sender": "operator",
                "text": "Patrol będzie na miejscu za około 15 minut.",
            },
            {"id": 5, "sender": "user", "text": "Dziękuję za pomoc."},
            {"id": 6, "sender": "operator", "text": "Do widzenia."},
        ]

    def _get_current_date(self) -> str:
        """Get current date in Polish format."""
        from datetime import datetime

        from django.utils import timezone

        months_pl = {
            1: "stycznia",
            2: "lutego",
            3: "marca",
            4: "kwietnia",
            5: "maja",
            6: "czerwca",
            7: "lipca",
            8: "sierpnia",
            9: "września",
            10: "października",
            11: "listopada",
            12: "grudnia",
        }

        now = timezone.now()
        return f"{now.day} {months_pl[now.month]} {now.year} r."
