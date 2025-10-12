Markdown

# Specyfikacja Techniczna Produktu (PRD v2.1) - Somsiad

> **Kontekst dla AI:** Poniższy dokument został wygenerowany w odpowiedzi na prośbę użytkownika, który buduje zaawansowany system RAG w Django. Użytkownik, wcielający się w rolę klienta, poprosił o stworzenie specyfikacji technicznej, która precyzyjnie opisuje budowany system, jego architekturę i parametry. Dokument ten ma służyć jako szczegółowy kontekst dla dalszych prac programistycznych i jest przeznaczony dla zaawansowanego odbiorcy technicznego.

## 1. Wprowadzenie i Cele

### 1.1. Wizja Produktu
**Somsiad** to precyzyjny, oparty na AI, asystent prawny dla właścicieli domów jednorodzinnych w Polsce. Aplikacja rozwiązuje problem rozproszonej i niezrozumiałej informacji prawnej, dostarczając natychmiastowych, kontekstowych odpowiedzi opartych na zaawansowanym, semantycznym silniku RAG.

### 1.2. Cele Technologiczne
* **Główny Cel:** Zbudowanie i wdrożenie produkcyjnej jakości, zaawansowanego systemu RAG, demonstrującego wyższość semantycznego przetwarzania dokumentów nad naiwnym chunkowaniem.
* **Architektura:** Stworzenie skalowalnego, bezstanowego backendu Django zoptymalizowanego pod kątem obsługi zapytań LLM w czasie rzeczywistym.
* **UX:** Dostarczenie interfejsu użytkownika opartego na SSE (Server-Sent Events) dla natychmiastowego feedbacku (streaming), zbliżonego do najnowocześniejszych rozwiązań na rynku.

---

## 2. Architektura Systemu

### 2.1. Stos Technologiczny
* **Backend:** Django 5.2.7
* **Frontend:** HTMX 1.9.10, Alpine.js 3.x, Tailwind CSS
* **Baza Danych (Główna):** PostgreSQL (zarządzany przez Supabase)
* **Baza Danych (Wektorowa):** Supabase z rozszerzeniem `pgvector`
* **AI / LLM:**
    * **Embeddingi:** OpenAI `text-embedding-3-small` (1536 wymiarów)
    * **Generowanie (Odpowiedzi i Podsumowania):** OpenAI `gpt-4o-mini`
* **Orkiestracja AI:** Własna implementacja serwisów (`RAGService`, `DocumentProcessor`); inspiracja konceptami LangChain.
* **Uwierzytelnianie:** `django-allauth` 65.11.2
* **Infrastruktura (CI/CD & Hosting):** GitHub Actions, Vercel/Railway

### 2.2. Kluczowe Parametry i Konfiguracja
Poniższe parametry definiują zachowanie rdzenia systemu RAG i są zarządzane centralnie.

| Parametr | Wartość | Opis | Źródło |
| :--- | :--- | :--- | :--- |
| **Model Embeddingów** | `text-embedding-3-small` | Model OpenAI do generowania wektorów. | |
| **Wymiar Wektora** | 1536 | Długość wektora embeddingu. | |
| **Model Generujący** | `gpt-4o-mini` | Model LLM do generowania odpowiedzi i podsumowań. | |
| **Temperatura LLM** | 0.3 | Kreatywność odpowiedzi (niska dla zachowania wierności faktom). | |
| **Metryka Podobieństwa** | `cosine` | Miara do porównywania wektorów w Supabase. | |
| **Liczba Kontekstów (`top_k`)** | 5 | Liczba fragmentów pobieranych z bazy wektorowej. | |
| **Maks. Rozmiar Chunka** | 1500 znaków | Granica, po której zbyt długi artykuł jest dzielony. | |

### 2.3. Potok Przetwarzania Dokumentów (Ingestia)
Przepływ danych od momentu przesłania pliku PDF do jego dostępności w systemie RAG.

```mermaid
graph TD
    A[Start: Admin przesyła PDF] --> B{Zapis w Django};
    B --> C[Uruchomienie DocumentProcessor];
    C --> D[1. Ekstrakcja tekstu (PyPDF2)];
    D --> E[2. Preprocessing (DocumentPreprocessor)];
    E --> F[3. Generowanie podsumowania (DocumentSummarizer)];
    F --> G[4. Semantyczne chunkowanie (SemanticChunker)];
    G --> H[5. Wzbogacanie metadanych];
    H --> I[6. Generowanie embeddingów (OpenAI API)];
    I --> J{Zapis w bazach danych};
    J --> K[Supabase: embedding, content, metadata];
    J --> L[Django: referencja do dokumentu i chunków];
    L --> M[Koniec: Dokument gotowy do odpytywania];
    K --> M;

    style F fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
2.4. Potok Wnioskowania (Generowanie Odpowiedzi)
Przepływ danych od zapytania użytkownika do otrzymania odpowiedzi.

Fragment kodu

graph TD
    A[Start: Użytkownik wysyła zapytanie] --> B{API Endpoint: /api/query/stream/};
    B --> C[1. Tworzenie embeddingu zapytania (OpenAI API)];
    C --> D[2. Wyszukiwanie wektorowe w Supabase];
    D -- RPC: match_embeddings(query_embedding, top_k=5) --> E[3. Pobranie 5 najbardziej podobnych chunków];
    E --> F[4. Budowa promptu (kontekst + pytanie)];
    F --> G[5. Streaming odpowiedzi (GPT-4o-mini)];
    G -- Server-Sent Events (SSE) --> H{Aktualizacja UI w czasie rzeczywistym};
    G --> I[6. Zapis zapytania i odpowiedzi w Django DB];
    H --> J[Koniec: Użytkownik widzi pełną odpowiedź];
    I --> J;

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
3. Szczegółowe Wymagania Funkcjonalne (FR)
FR-1: Zaawansowany Silnik RAG
FR-1.1: Preprocessing Tekstu: Serwis DocumentPreprocessor musi usuwać z surowego tekstu elementy administracyjne, takie jak "Kancelaria Sejmu", "Dziennik Ustaw", daty, podpisy, oraz korygować popularne błędy kodowania znaków.

FR-1.2: Semantyczne Chunkowanie: Serwis SemanticChunker musi dzielić dokumenty w oparciu o wyrażenia regularne identyfikujące logiczne separatory, takie jak "Art. [numer].", "§ [numer].", "Rozdział [numer]". W przypadku braku dopasowania stosowany jest podział awaryjny o stałej długości.

FR-1.3: Hierarchiczne Podsumowania: Serwis DocumentSummarizer musi, używając gpt-4o-mini, generować 3-częściowe podsumowanie dokumentu (STRESZCZENIE, KLUCZOWE TEMATY, ZAKRES ZASTOSOWANIA), które następnie jest zapisywane jako osobny, przeszukiwalny chunk.

FR-1.4: Wzbogacanie Metadanych: Podczas chunkowania, każdy fragment musi zostać wzbogacony o zbiór metadanych w formacie JSONB, zawierający m.in.: article_references, measurements, contains_obligations, article_number, section_name.

FR-2: Interfejs Konwersacyjny
FR-2.1: Streaming Odpowiedzi (SSE): Endpoint /api/query/stream/ musi wykorzystywać StreamingHttpResponse Django do wysyłania odpowiedzi w formacie Server-Sent Events, co pozwala na aktualizację DOM po stronie klienta słowo po słowie.

FR-2.2: Zarządzanie Konwersacjami: System musi udostępniać pełne API (CRUD) do zarządzania konwersacjami (/api/conversations/...), pozwalając na ich tworzenie, listowanie, wczytywanie i usuwanie. Historia jest renderowana za pomocą partiali HTMX.

FR-3: Zarządzanie Bazą Wiedzy
FR-3.1: Przetwarzanie Asynchroniczne (Symulowane): Wywołanie akcji "Przetwórz" z UI musi zwracać natychmiastowy feedback (spinner), mimo że samo przetwarzanie odbywa się synchronicznie w ramach żądania. Długotrwałe operacje powinny zostać w przyszłości przeniesione do dedykowanego workera (np. Celery).

4. Wymagania Niefunkcjonalne (NFR)
NFR-1: Wydajność:

TTFT (Time To First Token): Czas od wysłania zapytania do odebrania przez klienta pierwszego tokenu odpowiedzi musi być niższy niż 5 sekund (P95).

Czas Przetwarzania Dokumentu: Czas od przesłania do zakończenia ingestii dokumentu o objętości 50 stron powinien mieścić się w przedziale 10-30 sekund.

NFR-2: Bezpieczeństwo:

Wszystkie klucze API i sekrety muszą być zarządzane przez zmienne środowiskowe (.env w trybie deweloperskim) i nigdy nie mogą być częścią repozytorium kodu.

Klucz service_role Supabase NIGDY nie może być używany po stronie aplikacji klienckiej; dozwolony jest jedynie klucz anon public.

Aplikacja musi być zabezpieczona przed podstawowymi atakami webowymi (XSS, CSRF) z wykorzystaniem wbudowanych mechanizmów Django.

NFR-3: Testowalność:

Pokrycie kodu testami (unit, integration) musi wynosić >70%.

Muszą istnieć co najmniej 2 testy E2E (Playwright/Selenium) sprawdzające kluczowe ścieżki: (1) Rejestracja -> Zapytanie -> Odpowiedź; (2) Upload dokumentu -> Zapytanie z jego kontekstu.

5. Schemat Bazy Danych i API
5.1. Modele Django
Python

# knowledge/models.py
class Document(models.Model):
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    # ...

class Embedding(models.Model):
    document = models.ForeignKey(Document, related_name='embeddings')
    chunk_text = models.TextField()
    embedding_id = models.CharField(max_length=100)  # Supabase UUID
    metadata = models.JSONField()
    # ...

# queries/models.py
class Conversation(models.Model):
    user = models.ForeignKey(User, related_name='conversations')
    title = models.CharField(max_length=255)
    # ...

class Query(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='queries')
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField()
    # ...

5.2. Schemat Supabase (pgvector)
SQL

-- Wymagane rozszerzenie
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela na embeddingi
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    embedding VECTOR(1536),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indeks dla szybkiego wyszukiwania
CREATE INDEX ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Funkcja do wyszukiwania semantycznego
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_count INT
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.content,
        e.metadata,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM embeddings e
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

5.3. Kluczowe Endpoints API
Metoda	Endpoint	Opis
POST	/api/query/stream/	Przesyła zapytanie i zwraca strumień SSE z odpowiedzią.
POST	/api/conversations/create/	Tworzy nową konwersację.
GET	/api/conversations/list/	Zwraca listę konwersacji użytkownika.
GET	/api/conversations/<id>/	Wczytuje wiadomości z danej konwersacji.
DELETE	/api/conversations/<id>/delete/	Usuwa konwersację.
POST	/documents/upload/	Przesyła nowy dokument PDF.
POST	/documents/<id>/process/	Uruchamia proces ingestii dla dokumentu.	
