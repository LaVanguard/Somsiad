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

### 2.1. Stos Technologiczny (Kompletny)

#### Backend Framework & Core
* **Django:** 5.2.7 - główny framework webowy
* **Django REST Framework:** 3.16.1 - API endpoints
* **Python:** 3.12+ (runtime.txt)
* **WSGI Server:** Gunicorn 23.0.0 (produkcja, Unix/Linux only)
* **Configuration:** python-decouple 3.8

#### Frontend Stack
* **HTMX:** 1.9.10 - interaktywność bez JavaScript
* **Alpine.js:** 3.x - reaktywność (chat interface, sidebars)
* **Tailwind CSS:** styling i responsive design
* **Template Engine:** Django Templates (Jinja2-like)

#### Bazy Danych
* **Główna (Django ORM):** PostgreSQL via Supabase
* **Wektorowa:** Supabase pgvector extension
* **Development:** SQLite (fallback)
* **Database URL Parser:** dj-database-url 2.2.0

#### AI / LLM Stack
* **Embeddingi:** OpenAI `text-embedding-3-small` (1536 wymiarów)
* **Generowanie:** OpenAI `gpt-4o-mini` (temperatura: 0.3)
* **Orkiestracja:** LangChain 0.3.7, LangChain-OpenAI 0.2.9
* **Tokenizacja:** tiktoken 0.8.0
* **PDF Processing:** PyPDF2 3.0.1
* **Vector DB Client:** supabase 2.10.0

#### Uwierzytelnianie & Bezpieczeństwo
* **Auth System:** django-allauth 65.11.2 (email-based login)
* **CSRF Protection:** Django built-in
* **Session Security:** Secure cookies, HSTS headers
* **Password Hashing:** Django default (PBKDF2)

#### Static Files & Media
* **Static Files Server:** WhiteNoise 6.11.0 (compressed, cached)
* **Image Handling:** Pillow 11.0.0
* **Storage:** Django FileSystemStorage (media/documents/)

#### Testing & Quality
* **Test Framework:** pytest 8.4.2, pytest-django 4.11.1
* **E2E Testing:** Playwright 1.55.0, pytest-playwright 0.7.1
* **Coverage:** pytest-cov 6.0.0
* **Code Quality:** black 24.10.0, flake8 7.1.1, isort 5.13.2
* **Security Scanning:** bandit 1.7.10, safety 3.2.11

#### Infrastructure & Deployment
* **CI/CD:** GitHub Actions
* **Production Platform:** Railway / Heroku / Render (recommended: Railway)
* **Environment Management:** .env files (development), platform variables (production)
* **Logging:** Django logging to console + files (production)

#### Dependencies Management
* **Package Manager:** pip
* **Requirements:** requirements.txt (pinned versions)
* **Total Dependencies:** ~51 packages (including sub-dependencies)

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

### 5.3. API Endpoints - Kompletna Specyfikacja

#### Autentykacja (django-allauth)
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| GET | `/accounts/login/` | Formularz logowania | No | HTML |
| POST | `/accounts/login/` | Login użytkownika (email + password) | No | Redirect |
| GET | `/accounts/signup/` | Formularz rejestracji | No | HTML |
| POST | `/accounts/signup/` | Rejestracja nowego użytkownika | No | Redirect |
| GET | `/accounts/logout/` | Wylogowanie (GET allowed) | Yes | Redirect |
| GET/POST | `/accounts/password/reset/` | Reset hasła | No | HTML/Email |

**Login Form Fields:**
- `login` (email) - pole email (NOT username!)
- `password` - hasło
- `remember` - zapamiętaj mnie (optional)

---

#### RAG Query API
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| POST | `/api/query/` | **[DEPRECATED]** Legacy JSON query | Yes | JSON |
| POST | `/api/query/stream/` | **Streaming RAG query** (SSE) | Yes | text/event-stream |

**POST /api/query/stream/** - Primary endpoint
```json
// Request (multipart/form-data)
{
  "question": "Jakie są przepisy dotyczące budowy?",
  "conversation_id": 123,  // optional, null = new conversation
  "image": <file>           // optional, future feature
}

// Response (Server-Sent Events stream)
data: {"chunk": "Zgodnie", "conversation_id": 123}
data: {"chunk": " z przepisami..."}
data: {"chunk": " budowlanymi..."}
data: {"done": true, "sources": [...], "processing_time": 2.34}
```

**SSE Event Types:**
- `chunk` - fragment odpowiedzi (streaming text)
- `conversation_id` - ID utworzonej/używanej konwersacji
- `sources` - lista dokumentów źródłowych (na końcu)
- `processing_time` - czas generowania odpowiedzi (sekundy)
- `error` - komunikat błędu (jeśli wystąpił)
- `done` - flaga zakończenia streamu

---

#### Conversation Management API
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| POST | `/api/conversations/create/` | Tworzy nową konwersację | Yes | JSON |
| GET | `/api/conversations/list/` | Lista konwersacji użytkownika | Yes | HTML (HTMX partial) |
| GET | `/api/conversations/<id>/` | Ładuje wiadomości z konwersacji | Yes | HTML (HTMX partial) |
| DELETE | `/api/conversations/<id>/delete/` | Usuwa konwersację | Yes | HTTP 200 (empty) |

**POST /api/conversations/create/**
```json
// Request: empty body
// Response:
{
  "success": true,
  "conversation_id": 123,
  "title": "Nowa rozmowa"
}
```

**GET /api/conversations/list/**
- Returns: HTML partial (`partials/conversations_list.html`)
- Grouped by: today, yesterday, older
- Used by: HTMX (`hx-get`)

**GET /api/conversations/<id>/**
- Returns: HTML partial (`partials/conversation_messages.html`)
- Includes: all Query objects with question/answer/sources

**DELETE /api/conversations/<id>/delete/**
- Returns: Empty 200 OK (for HTMX swap)
- Side effect: Deletes all related Query objects (CASCADE)

---

#### Document Management API
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| POST | `/api/documents/upload/` | Przesyła PDF do systemu | Yes | HTML (message partial) |
| GET | `/api/documents/list/` | Lista dokumentów (filtered) | Yes | HTML (HTMX partial) |
| POST | `/api/documents/<id>/process/` | Przetwarza dokument (RAG pipeline) | Yes | HTML (message partial) |
| POST | `/api/documents/<id>/reprocess/` | Ponownie przetwarza dokument | Yes | HTML (message partial) |
| DELETE | `/api/documents/<id>/delete/` | Usuwa dokument + embeddingi | Yes | HTML (message partial) |
| POST | `/api/documents/process-all/` | Przetwarza wszystkie nieprzetworzone | Yes | HTML (message partial) |

**POST /api/documents/upload/**
```json
// Request (multipart/form-data)
{
  "title": "Prawo budowlane",
  "category": "budowa",  // budowa | ochrona_przyrody | przeglady
  "file": <PDF file>
}

// Response: HTML message
"<div class='text-green-400'>[SUCCESS] Dokument dodany: Prawo budowlane.pdf</div>"
```

**GET /api/documents/list/?status=processed|unprocessed**
- Returns: HTML partial (`partials/processed_documents.html` or `partials/unprocessed_documents.html`)
- Each document card includes:
  - Title, category, upload date
  - Process/Reprocess/Delete buttons (HTMX)

**POST /api/documents/<id>/process/**
- Triggers: Full RAG pipeline (DocumentProcessor)
- Steps:
  1. Extract text (PyPDF2)
  2. Preprocess (remove admin noise)
  3. Generate summary (GPT-4o-mini)
  4. Semantic chunking
  5. Metadata enrichment
  6. Generate embeddings (OpenAI)
  7. Store in Supabase + Django
- Duration: ~10-30 seconds (50-page document)
- Returns: Success/error message (HTML)

---

#### Profile & Settings API
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| GET | `/api/profile/` | Pobiera sidebar profilu użytkownika | Yes | HTML (HTMX partial) |
| POST | `/api/profile/update-prompt/` | Aktualizuje system prompt użytkownika | Yes | JSON |

**GET /api/profile/**
- Returns: HTML partial (`partials/profile_sidebar.html`)
- Includes:
  - Username, email
  - System prompt textarea
  - Conversation count
  - Document count

**POST /api/profile/update-prompt/**
```json
// Request
{
  "system_prompt": "Jesteś asystentem prawnym..."
}

// Response
{
  "success": true,
  "message": "Prompt zaktualizowany"
}
```

---

#### Static Pages
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| GET | `/` | Główna strona (chat interface) | Yes | HTML |
| GET | `/admin/` | Django Admin Panel | Yes (superuser) | HTML |

**GET /** (home)
- Requires: `@login_required` decorator
- Redirects: unauthenticated users → `/accounts/login/`
- Template: `home.html`
- Features:
  - Left sidebar: Conversations + Documents (tabs)
  - Main area: Chat interface with SSE streaming
  - Right sidebar: Profile (HTMX loaded)
  - Bottom bar: Message input + image upload

---

#### Internal/Admin Only
| Metoda | Endpoint | Opis | Auth Required | Response Type |
|--------|----------|------|---------------|---------------|
| GET | `/admin/` | Django Admin Panel | Yes (staff) | HTML |

**Note:** All API endpoints starting with `/api/` use either:
- **JSON responses** (for programmatic access)
- **HTML partials** (for HTMX dynamic updates)
- **SSE streams** (for real-time streaming)

**HTMX Integration:**
- All document/conversation management uses HTMX
- No page reloads, only partial DOM updates
- Error messages rendered as HTML partials
- Spinners via `hx-indicator`

**Authentication:**
- All endpoints except `/accounts/*` require `@login_required`
- AJAX endpoints use `@ajax_login_required` (returns 401 instead of redirect)
- CSRF protection via `{% csrf_token %}` in forms

---

## 6. Interfejs Użytkownika (Frontend)

### 6.1. Architektura Frontend

**Filozofia:** Modern, minimalist chat interface inspirowany Claude/ChatGPT/Gemini

**Technologie:**
- **HTMX 1.9.10** - dynamiczne aktualizacje bez JavaScript
- **Alpine.js 3.x** - reaktywność (sidebars, chat state)
- **Tailwind CSS** - utility-first styling
- **Django Templates** - server-side rendering

**Responsywność:**
- Desktop-first design
- Mobile sidebars (overlay with backdrop)
- Breakpoints: lg (1024px+)

---

### 6.2. Ekrany i Komponenty

#### 6.2.1. Login Page (`/accounts/login/`)

**Layout:**
- Centered card na szarym tle
- Logo "Somsiad" (z typo) na górze
- Formularz email + hasło
- Link do rejestracji
- Link do reset hasła

**Pola formularza:**
- `login` (type: email) - **UWAGA:** pole nazywa się "login", nie "username"!
- `password` (type: password)
- `remember` (checkbox) - zapamiętaj mnie

**Styling:**
- Tailwind CSS
- Focus states (ring-2 ring-blue-500)
- Error messages (django-allauth)

---

#### 6.2.2. Main Chat Interface (`/` - home)

**Layout:** 3-column fixed layout (sidebars + main area)

```
┌─────────────┬──────────────────────┬─────────────┐
│  Left       │   Main Chat Area     │   Right     │
│  Sidebar    │                      │   Profile   │
│  (320px)    │   (flex-1)           │   (384px)   │
│             │                      │             │
│ [Tabs]      │  [Welcome/Messages]  │ [User Info] │
│ Conv/Docs   │                      │ [Settings]  │
│             │  [Input Bar]         │             │
└─────────────┴──────────────────────┴─────────────┘
```

**Kolory:**
- Background główny: `bg-gray-100` (jasny szary)
- Sidebary: `bg-gray-800` (ciemny szary)
- Top nav: `bg-gray-800` (ciemny szary)
- Input bar: `bg-gray-800` (ciemny szary)
- User message bubble: `bg-blue-600` (niebieski)
- AI message bubble: `bg-white` (biały z shadow)

---

#### 6.2.3. Top Navigation Bar

**Elementy (left → right):**
1. **Hamburger Menu** (toggle left sidebar)
   - Icon: 3 poziome kreski
   - Hover: `bg-gray-700`

2. **Logo + "Somsiad"** (center)
   - Logo: `static/images/logo.png`
   - Font: semibold, text-xl

3. **User Avatar** (right, toggle right sidebar)
   - Circle: `bg-gray-600`
   - Icon: user SVG
   - Click: loads `/api/profile/` via HTMX

**Height:** py-3 (48px)
**Border:** `border-b border-gray-700`

---

#### 6.2.4. Left Sidebar (Conversations + Documents)

**Struktura:**
```
┌─────────────────────┐
│ Header + Close Btn  │ ← "Somsiad" logo + X
├─────────────────────┤
│ [Rozmowy│Dokumenty] │ ← Tabs (2)
├─────────────────────┤
│                     │
│   Tab Content       │ ← Dynamic (scrollable)
│   (HTMX loaded)     │
│                     │
├─────────────────────┤
│ Footer (Logout)     │ ← Link do wylogowania
└─────────────────────┘
```

**Tab 1: Rozmowy (Conversations)**
- **"Nowa rozmowa" button** (zawsze na górze)
  - Icon: plus
  - Click: czyści chat, resetuje `currentConversationId`

- **Conversations List** (`#conversations-list`)
  - Loaded via HTMX: `hx-get="/api/conversations/list/"`
  - Grouped by:
    - **Dziś** (today)
    - **Wczoraj** (yesterday)
    - **Starsze** (older)

- **Conversation Card:**
  - Title (truncated)
  - First message preview (truncated)
  - Click: loads conversation via HTMX
  - Hover: `bg-gray-600`
  - Delete icon (trash) on hover

**Tab 2: Dokumenty (Documents)**
- **Upload Form:**
  - Tytuł (text input)
  - Kategoria (select):
    - `budowa` - Budowa
    - `ochrona_przyrody` - Ochrona przyrody
    - `przeglady` - Przeglądy
  - Plik PDF (file input)
  - Submit button: "Dodaj PDF"

- **Processed Documents** (`#processed-list`)
  - Header: "Przetworzone (X)" + Odśwież button
  - HTMX load: `/api/documents/list/?status=processed`
  - Each card:
    - Icon: 📄
    - Title + category badge
    - Upload date
    - Actions: Reprocess, Delete

- **Unprocessed Documents** (`#unprocessed-list`)
  - Header: "Nieprzetworzone (X)" + "Przetwórz wszystkie"
  - HTMX load: `/api/documents/list/?status=unprocessed`
  - Each card:
    - Icon: 📄 (gray)
    - Title + category badge
    - **Przetwórz button** (primary action)
    - Delete button

**Footer:**
- Logout link (icon + text)
- Hover: `bg-gray-700`

**Mobile Behavior:**
- Sidebar overlay (fixed, z-50)
- Slide-in animation (translateX)
- Backdrop overlay (`bg-black bg-opacity-50`)

---

#### 6.2.5. Main Chat Area

**States:**

**1. Welcome State** (empty chat)
```
       ┌────────────┐
       │  Logo 🤖   │  (large, opacity-60)
       └────────────┘

   Witaj w Somsiad

   Zadaj pytanie o przepisy
   budowlane i prawne
```

**2. Chat State** (with messages)
```
┌─────────────────────────────┐
│ User Message (right-aligned)│  ← blue bubble
└─────────────────────────────┘

┌─────────────────────────────┐
│ AI Response (left-aligned)  │  ← white bubble
│ [Somsiad icon + name]       │
│ Odpowiedź...                │
│ ─────────────────────       │
│ Źródła:                     │  ← collapsed by default
│ 📄 Prawo budowlane - Art.1  │
│ Czas: 2.34s                 │  ← processing time
└─────────────────────────────┘
```

**Message Bubble Styling:**
- **User (right):**
  - `bg-blue-600 text-white`
  - `rounded-2xl px-5 py-3`
  - Max width: 600px

- **AI (left):**
  - `bg-white rounded-2xl px-5 py-4 shadow-sm`
  - Max width: 768px
  - Header: Somsiad icon + bold name
  - Content: `prose prose-sm` (typography)
  - Sources: border-top, collapsed initially
  - Time: `text-xs text-gray-400`

**Scrolling:**
- Auto-scroll to bottom on new message
- Custom scrollbar (thin, gray)

---

#### 6.2.6. Bottom Input Bar

**Layout:**
```
┌────────────────────────────────────────────┐
│  [📷]  [Textarea Input]  [Wyślij ➤]       │
│  Image  (flex-grow)       Button           │
└────────────────────────────────────────────┘
```

**Komponenty:**

**1. Image Upload Button** (left)
- Icon: 📷 (photo SVG)
- Click: opens file picker
- Accepts: `image/*`
- Preview: shows above input bar
- Remove: X button on preview

**2. Textarea Input** (center)
- Placeholder: "Zadaj pytanie o przepisy budowlane..."
- Auto-resize (min: 56px, max: 200px)
- Enter: submit (Shift+Enter: new line)
- Disabled during `loading` state
- Styling:
  - `bg-transparent text-white`
  - `placeholder-gray-400`
  - No border, no outline

**3. Send Button** (right)
- Text: "Wyślij" + send icon ➤
- States:
  - **Active:** `bg-blue-600 hover:bg-blue-700`
  - **Disabled:** `bg-gray-600 opacity-50 cursor-not-allowed`
  - **Loading:** spinning icon
- Disabled when:
  - Input empty AND no image
  - Already loading

**Container Styling:**
- `bg-gray-700 rounded-2xl p-2`
- Border: `border border-gray-600`
- Shadow: `shadow-lg`

**Background Bar:**
- `bg-gray-800 border-t border-gray-700 px-6 py-6`
- Shadow: `shadow-2xl`

---

#### 6.2.7. Right Sidebar (Profile)

**Structure:**
```
┌─────────────────────┐
│ Close Button (X)    │
├─────────────────────┤
│ User Avatar         │ ← Circle with initials
│ Email               │
│ Username            │
├─────────────────────┤
│ System Prompt       │ ← Textarea (editable)
│ [Save Prompt]       │
├─────────────────────┤
│ Stats:              │
│ ✉️  X conversations │
│ 📄 X documents      │
└─────────────────────┘
```

**Load:** HTMX on demand (`hx-get="/api/profile/"`)
**Width:** 384px (w-96)
**Mobile:** Slide-in overlay (same as left sidebar)

**System Prompt:**
- Textarea: 6 rows
- Placeholder: "Dostosuj zachowanie asystenta..."
- Save button: `hx-post="/api/profile/update-prompt/"`
- Success message: green, 2 seconds

---

### 6.3. Interaktywność (Alpine.js State)

**Global State** (via `x-data` on root div):
```javascript
{
  question: '',                   // current input value
  loading: false,                 // SSE streaming state
  imagePreview: null,             // base64 image preview
  imageFile: null,                // File object
  sidebarOpen: false,             // left sidebar visibility
  profileOpen: false,             // right sidebar visibility
  activeTab: 'conversations',     // left sidebar tab
  currentConversationId: null,    // active conversation
  currentAnswer: '',              // streaming answer buffer
  streamingMessageId: null        // ID of message being streamed
}
```

**Key Functions:**
- `submitStreamingQuery()` - handles SSE fetch + DOM updates
- `escapeHtml(text)` - XSS protection for user input

---

### 6.4. Streaming (Server-Sent Events)

**Flow:**
1. User submits form (`@submit.prevent="submitStreamingQuery"`)
2. Hide welcome state, show user message bubble
3. Create empty AI message bubble with loading indicator (`●`)
4. Fetch `/api/query/stream/` (POST, multipart/form-data)
5. Read SSE stream:
   - `data: {"chunk": "..."}` → append to `#ai-msg-123-text`
   - `data: {"conversation_id": 123}` → update Alpine state
   - `data: {"sources": [...]}` → render sources section
   - `data: {"done": true}` → stop spinner, refresh conversations
6. Auto-scroll to bottom after each chunk
7. On completion: refresh conversations list via HTMX

**Error Handling:**
- Network error: "❌ Błąd połączenia"
- Server error: "❌ " + error message from SSE

---

### 6.5. Templates Struktura

**Main Templates:**
- `base.html` - base layout (head, scripts, body wrapper)
- `home.html` - main chat interface (extends base)
- `account/login.html` - login page (django-allauth)
- `account/password_reset.html` - password reset

**Partials (HTMX):**
- `partials/conversations_list.html` - list of conversations (grouped)
- `partials/conversation_messages.html` - messages from one conversation
- `partials/processed_documents.html` - list of processed docs
- `partials/unprocessed_documents.html` - list of unprocessed docs
- `partials/profile_sidebar.html` - user profile sidebar
- `partials/message.html` - success/error message component

---

### 6.6. Static Files

**Images:**
- `static/images/logo.png` - Somsiad logo (8x8, 24x24 variants)

**CSS:**
- Tailwind CSS (CDN via `<script src="https://cdn.tailwindcss.com"></script>`)
- Custom scrollbar styles (inline in `home.html`)

**JavaScript:**
- HTMX 1.9.10 (CDN)
- Alpine.js 3.x (CDN)
- Custom: `submitStreamingQuery()` function (inline)

**Fonts:**
- System fonts (Inter fallback)

---

### 6.7. UX Features

**1. Real-time Streaming:**
- Word-by-word AI response
- Smooth scrolling
- Loading indicator (pulsing dot)

**2. Conversation Management:**
- One-click conversation load
- Auto-refresh after query
- Grouped by date (today/yesterday/older)

**3. Document Upload:**
- Drag & drop (file input)
- Instant feedback (HTMX messages)
- Processing spinner
- Bulk process ("Przetwórz wszystkie")

**4. Keyboard Shortcuts:**
- Enter: submit message
- Shift+Enter: new line in textarea

**5. Mobile Responsiveness:**
- Sidebars as overlays
- Backdrop click to close
- Touch-friendly buttons

**6. Loading States:**
- Spinners for HTMX requests
- Disabled buttons during operations
- Streaming indicator (pulsing dot)

**7. Error Messages:**
- Inline in UI (green/red)
- Auto-dismiss after 5 seconds
- HTMX swap into `#document-status`

---

### 6.8. Accessibility

**ARIA Labels:**
- Buttons have descriptive text or `aria-label`
- Form inputs have `<label>` elements

**Keyboard Navigation:**
- Tab order: logical (menu → input → buttons)
- Enter/Escape for modals

**Color Contrast:**
- WCAG AA compliant (Tailwind defaults)
- Focus states: `ring-2 ring-blue-500`

**Screen Readers:**
- Semantic HTML (`<nav>`, `<main>`, `<button>`)
- Alt text for logo image

---

### 6.9. Browser Support

**Tested:**
- Chrome 120+ (primary)
- Firefox 120+
- Safari 17+
- Edge 120+

**Required Features:**
- ES6 (Alpine.js, fetch)
- Server-Sent Events (SSE)
- Flexbox & Grid (Tailwind)

**Not Supported:**
- IE11 (no Alpine.js, no fetch)

---

## 7. Podsumowanie Techniczne

**Stack:**
- Django 5.2.7 + PostgreSQL + Supabase pgvector
- OpenAI (embeddings + chat) + LangChain
- HTMX + Alpine.js + Tailwind CSS

**Architecture:**
- Monolithic Django app (3 apps: accounts, knowledge, queries)
- Server-side rendering (Django templates)
- HTMX for dynamic updates (no SPA)
- SSE for real-time streaming

**Deployment:**
- Railway (recommended) / Heroku / Render
- Gunicorn WSGI server
- WhiteNoise static files
- PostgreSQL database (Supabase)

**Testing:**
- 125 unit tests (pytest)
- 2 E2E tests (Playwright)
- 60% code coverage
- CI/CD via GitHub Actions

**Documentation:**
- PRD v2.1 (this file)
- 7 sprint completion docs
- DEPLOYMENT.md guide
- PRD_COMPLIANCE_STATUS.md

**Status:** ✅ Production Ready (95.5% PRD compliance)
