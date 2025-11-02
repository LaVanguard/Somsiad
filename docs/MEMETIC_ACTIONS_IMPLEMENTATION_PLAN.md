# 🎭 Memiczne Akcje Prawne - Plan Implementacji

**Data:** 2025-11-02
**Sprint:** 9 (post-RAG 2.0)
**Priorytet:** Medium (feature rozrywkowy z wartością edukacyjną)

---

## 📋 User Story

> **Jako user** chciałbym po informacji, że ktoś łamie przepisy albo czegoś mu nie wolno - otrzymać 3 memiczne przyciski: **Zgłaszam do prokuratury**, **Donos**, **Straż miejska**.
>
> Po kliknięciu:
> - **Prokuratura:** wygeneruj pismo i daj komunikat że wysyłasz to do prokuratora (zgłoszenie popełnienia przestępstwa)
> - **Donos:** mail do rady gminy + prośba o podgranie zdjęcia/pliku dźwiękowego w celu dokumentacji szkody
> - **Straż Miejska:** fikcyjny flow na telefonowanie do straży
>
> **Cel:** Memiczne akcje, które merytorycznie są poprawne, ale NIE wywołują realnej akcji - tylko pokazują ją userowi jako żart.

---

## 🎯 Aktualna Implementacja (Stan Obecny)

### Istniejące Komponenty:

**Frontend:** `templates/partials/message.html:55-97`
- ✅ 3 przyciski: Prokuratura, Donos, Straż Miejska
- ✅ HTMX POST do `/api/query/` z `action` parameter
- ✅ Ikony SVG dla każdego przycisku

**Backend:** `accounts/views.py:118-119, 344-374`
- ✅ Wykrywanie akcji: `if action in ['prokuratura', 'donos', 'straz']`
- ✅ Funkcja `_get_joke_response()` z prostymi template'ami
- ❌ Brak generowania przez LLM
- ❌ Brak interaktywnego flow
- ❌ Brak modali/upload

---

## 🚀 Nowa Implementacja - Szczegółowy Plan

### **Feature 1: Prokuratura - Profesjonalne Pismo**

#### Flow UX:
```
User klika "Zgłoś do Prokuratury"
    ↓
Modal pojawia się z:
  - Spinner "Generuję pismo do prokuratury..."
  - GPT-5 mini generuje formalne pismo
    ↓
Modal pokazuje:
  - Wygenerowane pismo (edytowalne textarea)
  - Przyciski: "Wyślij do Prokuratury" | "Anuluj"
    ↓
User klika "Wyślij"
    ↓
Fake loading animation (3-5s):
  - "Łączę z systemem e-PUAP..."
  - "Weryfikuję dane..."
  - "Wysyłam pismo..."
    ↓
Success message:
  - ✅ "Pismo wysłane do Prokuratury Rejonowej!"
  - "(To był żart 😄 - nic nie zostało wysłane)"
  - Przycisk "Pobierz PDF" (fake download)
```

#### Techniczne Szczegóły:

**Prompt do GPT-5 mini:**
```python
prompt = f"""Wygeneruj FORMALNE PISMO do Prokuratury Rejonowej zawiadamiające o popełnieniu przestępstwa.

Kontekst sprawy: {question}

Odpowiedź AI (dla kontekstu): {ai_answer}

Wymagania:
1. Nagłówek: "Do Prokuratury Rejonowej w [Miasto]"
2. Data i miejsce
3. Dane nadawcy: "Imię i Nazwisko, Adres" (placeholder)
4. Tytuł: "ZAWIADOMIENIE O POPEŁNIENIU PRZESTĘPSTWA"
5. Treść:
   - Zwięzły opis sytuacji (2-3 zdania)
   - Wskazanie przepisów które mogły zostać naruszone
   - Prośba o wszczęcie postępowania
6. Podpis: "Z poważaniem, [Obywatel]"
7. Stopka: "Art. 304 § 2 Kodeksu postępowania karnego - obowiązek zawiadomienia"

Format: Profesjonalny, rzeczowy, bez emocji.
"""
```

**Backend Endpoint:**
```python
# accounts/views.py

@require_http_methods(["POST"])
@login_required
def generate_prosecutor_letter(request):
    """Generate fake prosecutor letter using GPT-5 mini."""
    question = request.POST.get('question', '')
    ai_answer = request.POST.get('ai_answer', '')

    # Generate letter using GPT-5 mini
    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-5-mini",
        temperature=0.2  # Low for formal tone
    )

    letter = llm.invoke(PROSECUTOR_LETTER_PROMPT.format(
        question=question,
        ai_answer=ai_answer
    ))

    return JsonResponse({
        'letter': letter.content,
        'timestamp': timezone.now().isoformat()
    })
```

**Frontend Modal (HTMX + Alpine.js):**
```html
<!-- templates/partials/prosecutor_modal.html -->
<div x-show="showProsecutorModal"
     x-cloak
     class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
     @click.self="showProsecutorModal = false">

    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-800">
                ⚖️ Pismo do Prokuratury Rejonowej
            </h3>
            <button @click="showProsecutorModal = false" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <!-- Loading State -->
        <div x-show="generatingLetter" class="text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Generuję profesjonalne pismo...</p>
        </div>

        <!-- Generated Letter -->
        <div x-show="!generatingLetter && !sendingLetter" class="space-y-4">
            <textarea
                x-model="prosecutorLetter"
                rows="20"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm"
                placeholder="Wygenerowane pismo pojawi się tutaj..."
            ></textarea>

            <!-- Action Buttons -->
            <div class="flex gap-3 justify-end">
                <button
                    @click="showProsecutorModal = false"
                    class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
                    Anuluj
                </button>
                <button
                    @click="sendProsecutorLetter()"
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition">
                    📤 Wyślij do Prokuratury
                </button>
            </div>
        </div>

        <!-- Sending Animation -->
        <div x-show="sendingLetter" class="text-center py-8">
            <div class="animate-pulse space-y-3">
                <p class="text-gray-600" x-text="sendingMessage"></p>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full transition-all duration-1000"
                         :style="`width: ${sendingProgress}%`"></div>
                </div>
            </div>
        </div>

        <!-- Success Message -->
        <div x-show="letterSent" class="text-center py-8">
            <div class="mb-4 text-6xl">✅</div>
            <h4 class="text-xl font-bold text-green-600 mb-2">Pismo wysłane!</h4>
            <p class="text-gray-600 mb-4">
                Twoje zawiadomienie zostało przekazane do Prokuratury Rejonowej.
            </p>
            <p class="text-sm text-gray-500 italic">
                (To był żart 😄 - nic nie zostało wysłane naprawdę!)
            </p>
            <button
                @click="downloadPDF()"
                class="mt-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition">
                📥 Pobierz PDF
            </button>
        </div>
    </div>
</div>
```

**Alpine.js Logic:**
```javascript
// templates/home.html - add to x-data
prosecutorLetter: '',
showProsecutorModal: false,
generatingLetter: false,
sendingLetter: false,
letterSent: false,
sendingMessage: '',
sendingProgress: 0,

async generateProsecutorLetter(question, aiAnswer) {
    this.showProsecutorModal = true;
    this.generatingLetter = true;
    this.letterSent = false;

    // Call backend to generate letter
    const response = await fetch('/api/actions/prosecutor/generate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ question, aiAnswer })
    });

    const data = await response.json();
    this.prosecutorLetter = data.letter;
    this.generatingLetter = false;
},

async sendProsecutorLetter() {
    this.sendingLetter = true;
    this.sendingProgress = 0;

    // Fake sending animation
    const steps = [
        { msg: '📡 Łączę z systemem e-PUAP...', progress: 20, delay: 1000 },
        { msg: '🔐 Weryfikuję dane...', progress: 50, delay: 1500 },
        { msg: '📨 Wysyłam pismo...', progress: 80, delay: 1500 },
        { msg: '✅ Potwierdzam wysłanie...', progress: 100, delay: 1000 }
    ];

    for (const step of steps) {
        this.sendingMessage = step.msg;
        this.sendingProgress = step.progress;
        await new Promise(resolve => setTimeout(resolve, step.delay));
    }

    this.sendingLetter = false;
    this.letterSent = true;
},

downloadPDF() {
    // Fake PDF download
    alert('📥 PDF zostałby pobrany, ale to tylko symulacja! 😄');
}
```

---

### **Feature 2: Donos - Email z Upload**

#### Flow UX:
```
User klika "Wyślij anonimowy donos"
    ↓
Modal pojawia się z:
  - Spinner "Generuję email..."
  - GPT-5 mini generuje email-donos
    ↓
Modal pokazuje:
  - Wygenerowany email (edytowalny)
  - Upload zone: "Przeciągnij zdjęcie/nagranie jako dowód"
  - Podgląd uploadowanych plików
  - Przyciski: "Wyślij Donos" | "Anuluj"
    ↓
User dodaje pliki (opcjonalne)
    ↓
User klika "Wyślij"
    ↓
Fake loading animation (3-5s):
  - "Szyfrowanie załączników..."
  - "Wysyłam na skrzynkę gminy..."
  - "Kasowanie śladów..."
    ↓
Success message:
  - ✅ "Donos wysłany anonimowo!"
  - "Załączniki: 2 zdjęcia, 1 nagranie"
  - "(To był żart 😄 - nic nie zostało wysłane)"
```

#### Prompt do GPT-5 mini:
```python
prompt = f"""Wygeneruj ANONIMOWY EMAIL-DONOS do Rady Gminy/Urzędu Miasta.

Kontekst sprawy: {question}

Odpowiedź AI (dla kontekstu): {ai_answer}

Wymagania:
1. Temat: "Zgłoszenie nieprawidłowości - [krótki opis]"
2. Treść:
   - Grzeczne otwarcie ("Szanowni Państwo")
   - Opis problemu (2-3 zdania, bez emocji)
   - Wskazanie ewentualnych naruszeń przepisów
   - Prośba o dyskretną interwencję
   - "Załączam dokumentację fotograficzną/dźwiękową"
3. Podpis: "Z poważaniem, Zatroskany Mieszkaniec"
4. Stopka: "Email wysłany anonimowo"

Ton: Oficjalny ale nie zbyt formalny, bez agresji.
"""
```

#### Upload Component:
```html
<!-- File Upload Zone -->
<div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
    <input
        type="file"
        id="donos-files"
        multiple
        accept="image/*,audio/*,video/*"
        @change="handleDonosFiles($event)"
        class="hidden"
    >
    <label for="donos-files" class="cursor-pointer">
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        <p class="text-gray-600 mb-1">Przeciągnij pliki lub kliknij aby dodać</p>
        <p class="text-xs text-gray-400">Zdjęcia, nagrania audio/wideo jako dowód</p>
    </label>
</div>

<!-- File Preview List -->
<div x-show="donosFiles.length > 0" class="mt-4 space-y-2">
    <template x-for="(file, index) in donosFiles" :key="index">
        <div class="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
            <div class="flex items-center gap-3">
                <span class="text-2xl" x-text="getFileIcon(file.type)"></span>
                <div>
                    <p class="text-sm font-medium" x-text="file.name"></p>
                    <p class="text-xs text-gray-500" x-text="formatFileSize(file.size)"></p>
                </div>
            </div>
            <button @click="removeDonosFile(index)" class="text-red-500 hover:text-red-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    </template>
</div>
```

---

### **Feature 3: Straż Miejska - Fake Telefon**

#### Flow UX:
```
User klika "Zadzwoń po Straż Miejską"
    ↓
Modal pojawia się z:
  - Animacja telefonu (ringing)
  - Numer: "986 (Straż Miejska)"
  - Dźwięk dzwonienia (opcjonalnie)
    ↓
Po 2-3s "odebrania":
  - Avatar operatora
  - Tekst: "Straż Miejska, słucham"
  - Automatyczna "rozmowa" (fake):
    * "Dzień dobry, zgłaszam problem..."
    * [Opis z AI answer]
    * "Rozumiem, wysyłamy patrol"
  - Timer rozmowy (00:15, 00:30...)
    ↓
Zakończenie (po ~30s):
  - ✅ "Patrol wysłany!"
  - "Czas przybycia: ~15 minut"
  - "(To był żart 😄 - nie dzwoniliśmy naprawdę)"
```

#### Animacja Telefonu:
```html
<!-- Calling Animation -->
<div class="text-center py-8">
    <div class="relative inline-block">
        <!-- Phone Icon with Ring Animation -->
        <div class="animate-bounce">
            <svg class="w-24 h-24 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 15.5c-1.25 0-2.45-.2-3.57-.57-.35-.11-.74-.03-1.02.24l-2.2 2.2c-2.83-1.44-5.15-3.75-6.59-6.59l2.2-2.21c.28-.26.36-.65.25-1C8.7 6.45 8.5 5.25 8.5 4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.5c0-.55-.45-1-1-1z"/>
            </svg>
        </div>
        <!-- Pulsing Rings -->
        <div class="absolute inset-0 animate-ping opacity-25">
            <svg class="w-24 h-24 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
            </svg>
        </div>
    </div>

    <p class="text-xl font-bold mt-4">Dzwonię...</p>
    <p class="text-gray-600">986 - Straż Miejska</p>
</div>

<!-- Call In Progress -->
<div x-show="callConnected" class="space-y-4">
    <div class="flex items-center gap-4 bg-green-50 p-4 rounded-lg">
        <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
        </div>
        <div class="flex-1">
            <p class="font-semibold">Dyżurny Straży Miejskiej</p>
            <p class="text-sm text-gray-600">W trakcie rozmowy...</p>
        </div>
        <div class="text-right">
            <p class="text-sm font-mono text-gray-500" x-text="callTimer"></p>
        </div>
    </div>

    <!-- Fake Conversation -->
    <div class="space-y-3 max-h-64 overflow-y-auto">
        <template x-for="message in callMessages" :key="message.id">
            <div class="flex" :class="message.sender === 'user' ? 'justify-end' : 'justify-start'">
                <div class="max-w-xs px-4 py-2 rounded-lg"
                     :class="message.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'">
                    <p class="text-sm" x-text="message.text"></p>
                </div>
            </div>
        </template>
    </div>

    <button
        @click="endCall()"
        class="w-full bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg flex items-center justify-center gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.11-.7-.28-.79-.74-1.68-1.36-2.66-1.85-.33-.16-.56-.5-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
        </svg>
        Rozłącz
    </button>
</div>
```

**Alpine.js Call Logic:**
```javascript
callConnected: false,
callTimer: '00:00',
callSeconds: 0,
callMessages: [],
callInterval: null,

async startStrazCall(question, aiAnswer) {
    this.showStrazModal = true;
    this.callConnected = false;
    this.callMessages = [];
    this.callSeconds = 0;

    // Ringing phase (3 seconds)
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Call answered
    this.callConnected = true;
    this.callMessages.push({
        id: 1,
        sender: 'operator',
        text: 'Straż Miejska, słucham. W czym mogę pomóc?'
    });

    // Start call timer
    this.callInterval = setInterval(() => {
        this.callSeconds++;
        const mins = Math.floor(this.callSeconds / 60).toString().padStart(2, '0');
        const secs = (this.callSeconds % 60).toString().padStart(2, '0');
        this.callTimer = `${mins}:${secs}`;
    }, 1000);

    // User explains problem
    await new Promise(resolve => setTimeout(resolve, 2000));
    this.callMessages.push({
        id: 2,
        sender: 'user',
        text: `Dzień dobry, zgłaszam problem: ${question.substring(0, 100)}...`
    });

    // Operator responds
    await new Promise(resolve => setTimeout(resolve, 3000));
    this.callMessages.push({
        id: 3,
        sender: 'operator',
        text: 'Rozumiem sytuację. Wysyłam patrol do sprawdzenia.'
    });

    // Patrol info
    await new Promise(resolve => setTimeout(resolve, 2000));
    this.callMessages.push({
        id: 4,
        sender: 'operator',
        text: 'Patrol będzie na miejscu za około 15 minut. Czy mogę jeszcze w czymś pomóc?'
    });

    await new Promise(resolve => setTimeout(resolve, 2000));
    this.callMessages.push({
        id: 5,
        sender: 'user',
        text: 'Nie, dziękuję za pomoc.'
    });

    await new Promise(resolve => setTimeout(resolve, 1500));
    this.callMessages.push({
        id: 6,
        sender: 'operator',
        text: 'Do widzenia.'
    });

    // Auto end call after 2s
    setTimeout(() => this.endCall(), 2000);
},

endCall() {
    clearInterval(this.callInterval);
    this.callConnected = false;
    this.showCallEnded = true;
}
```

---

## 🏗️ Architektura Techniczna

### Backend (Django)

**Nowe Endpointy:**
```python
# config/urls.py
urlpatterns = [
    # ... existing
    path('api/actions/prosecutor/generate/', views.generate_prosecutor_letter),
    path('api/actions/donos/generate/', views.generate_donos_email),
    path('api/actions/straz/call/', views.simulate_straz_call),
]
```

**Nowe Serwisy:**
```
knowledge/services/
├── memetic_actions_service.py  # NEW
│   ├── generate_prosecutor_letter()
│   ├── generate_donos_email()
│   └── generate_straz_script()
```

**Zmiany w Views:**
```python
# accounts/views.py

# OLD (current):
if action in ['prokuratura', 'donos', 'straz']:
    answer = _get_joke_response(action, question)  # Simple template

# NEW (after implementation):
if action in ['prokuratura', 'donos', 'straz']:
    # Return special flag to trigger modal on frontend
    return JsonResponse({
        'action_triggered': True,
        'action_type': action,
        'question': question,
        'ai_answer': answer  # Full RAG answer for context
    })
```

### Frontend (HTMX + Alpine.js)

**Nowe Komponenty:**
```
templates/
├── partials/
│   ├── prosecutor_modal.html       # NEW
│   ├── donos_modal.html           # NEW
│   ├── straz_call_modal.html      # NEW
│   └── message.html               # MODIFIED (trigger modals)
```

**Alpine.js State Extensions:**
```javascript
// templates/home.html - add to x-data
{
    // Prosecutor
    showProsecutorModal: false,
    prosecutorLetter: '',
    generatingLetter: false,
    sendingLetter: false,
    letterSent: false,

    // Donos
    showDonosModal: false,
    donosEmail: '',
    donosFiles: [],

    // Straz
    showStrazModal: false,
    callConnected: false,
    callMessages: [],
    callTimer: '00:00',

    // Methods
    async generateProsecutorLetter(question, aiAnswer) { ... },
    async sendProsecutorLetter() { ... },
    async generateDonosEmail(question, aiAnswer) { ... },
    async startStrazCall(question, aiAnswer) { ... }
}
```

---

## 📊 Dane i Modele

**Czy zapisywać akcje w bazie?**

**Opcja A (Minimalna):** Nie zapisuj - tylko loguj w console
```python
logger.info(f"User {user.id} triggered {action} for query {query.id}")
```

**Opcja B (Pełna):** Zapisuj do bazy dla analytics
```python
# queries/models.py - ADD FIELD
class Query(models.Model):
    # ... existing fields
    memetic_action = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('prokuratura', 'Prokuratura'),
            ('donos', 'Donos'),
            ('straz', 'Straż Miejska')
        ],
        help_text="Memetic action triggered by user (if any)"
    )
    action_triggered_at = models.DateTimeField(null=True, blank=True)
```

**Rekomendacja:** Opcja B - daje analytics ("które akcje są najpopularniejsze?")

---

## 🎨 UX/UI Details

### Modals Design:
- **Backdrop:** `bg-black/50` (półprzezroczyste tło)
- **Modal:** `max-w-2xl` (średnia szerokość), `rounded-xl shadow-2xl`
- **Animacje:** `x-transition` (Alpine.js) dla smooth open/close
- **Responsywność:** Mobile-friendly (pełny ekran na telefonach)

### Loading States:
- **Spinner:** Tailwind `animate-spin`
- **Progress Bar:** Animated width transitions
- **Fake Steps:** 3-4 kroki z delays (1-2s każdy)

### Colors:
- **Prokuratura:** Blue (`blue-600`) - oficjalny, poważny
- **Donos:** Yellow/Orange (`orange-500`) - ostrzegawczy
- **Straż:** Green (`green-600`) - patrol, akcja

---

## 🧪 Testing Plan

### Unit Tests:
```python
# accounts/tests/test_memetic_actions.py

def test_prosecutor_letter_generation():
    """Test GPT-5 mini generates formal letter"""
    response = generate_prosecutor_letter(
        question="Sąsiad buduje bez pozwolenia",
        ai_answer="To naruszenie prawa budowlanego..."
    )
    assert "Prokuratury Rejonowej" in response['letter']
    assert "ZAWIADOMIENIE" in response['letter']

def test_donos_email_generation():
    """Test GPT-5 mini generates anonymous email"""
    response = generate_donos_email(
        question="Hałas z budowy o 22:00",
        ai_answer="Naruszenie cisz nocnej..."
    )
    assert "Szanowni Państwo" in response['email']
    assert "anonimowo" in response['email'].lower()

def test_straz_call_simulation():
    """Test fake call script generation"""
    response = simulate_straz_call(
        question="Nielegalne parkowanie",
        ai_answer="Może to naruszenie..."
    )
    assert len(response['messages']) > 0
    assert response['estimated_time'] == '~15 minut'
```

### E2E Tests (Playwright):
```python
# tests/e2e/test_memetic_actions.py

@pytest.mark.e2e
def test_prosecutor_action_flow(page, authenticated_user):
    """Test full prosecutor modal flow"""
    # Ask question that triggers illegal activity
    page.fill('textarea[name="question"]', 'Jak zgłosić nielegalną budowę?')
    page.click('button:has-text("Wyślij")')

    # Wait for response
    page.wait_for_selector('.ai-response')

    # Click prosecutor button
    page.click('button:has-text("Zgłoś do Prokuratury")')

    # Wait for modal
    page.wait_for_selector('[x-show="showProsecutorModal"]')

    # Wait for letter generation
    assert page.is_visible('text=Generuję pismo')
    page.wait_for_selector('textarea', timeout=10000)

    # Verify letter content
    letter = page.input_value('textarea')
    assert 'Prokuratury Rejonowej' in letter

    # Click send
    page.click('button:has-text("Wyślij do Prokuratury")')

    # Wait for fake sending animation
    assert page.is_visible('text=Łączę z systemem e-PUAP')

    # Verify success
    page.wait_for_selector('text=Pismo wysłane!', timeout=10000)
    assert page.is_visible('text=To był żart')
```

---

## 📅 Implementation Timeline

### Sprint 9 - Week 1:
**Day 1-2:** Prokuratura Feature
- ✅ Backend: `generate_prosecutor_letter()` endpoint
- ✅ Frontend: Modal component
- ✅ Alpine.js logic
- ✅ Tests

**Day 3-4:** Donos Feature
- ✅ Backend: `generate_donos_email()` endpoint
- ✅ Frontend: Modal with file upload
- ✅ File handling logic
- ✅ Tests

**Day 5:** Straż Feature
- ✅ Backend: `simulate_straz_call()` endpoint
- ✅ Frontend: Call animation modal
- ✅ Fake conversation flow
- ✅ Tests

### Sprint 9 - Week 2:
**Day 1-2:** Polish & Refinement
- 🎨 UI/UX improvements
- 🐛 Bug fixes
- 📱 Mobile responsiveness

**Day 3:** Integration Testing
- E2E tests
- Cross-browser testing
- Performance testing

**Day 4:** Documentation & Deployment
- Update user docs
- Deployment to staging
- QA testing

---

## 🚨 Edge Cases & Error Handling

### OpenAI API Failures:
```python
try:
    letter = llm.invoke(prompt)
except OpenAIError as e:
    # Fallback to template-based response
    logger.error(f"GPT-5 mini failed: {e}")
    return {
        'letter': FALLBACK_PROSECUTOR_TEMPLATE.format(question=question),
        'generated_by': 'template'
    }
```

### File Upload Limits:
```javascript
handleDonosFiles(event) {
    const files = Array.from(event.target.files);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const maxFiles = 5;

    if (files.length > maxFiles) {
        alert(`Maksymalnie ${maxFiles} plików!`);
        return;
    }

    for (const file of files) {
        if (file.size > maxSize) {
            alert(`Plik ${file.name} jest za duży (max 10MB)`);
            return;
        }
    }

    this.donosFiles = files;
}
```

### Modal Escape Key:
```html
<div @keydown.escape.window="showProsecutorModal = false">
```

---

## 💰 Cost Estimation

**GPT-5 mini API Calls:**
- Prosecutor letter: ~500 tokens input + 800 tokens output = ~$0.0003 per generation
- Donos email: ~400 tokens input + 600 tokens output = ~$0.0002 per generation
- Straz script: ~300 tokens input + 400 tokens output = ~$0.00015 per generation

**Assumed Usage:** 100 actions/day
- Daily cost: ~$0.03
- Monthly cost: ~$0.90

**Verdict:** 💰 Very cheap - negligible cost

---

## 🎯 Success Metrics

### KPIs:
1. **Action Usage Rate:** % of queries that trigger memetic actions
   - Target: 10-20% of all queries
2. **Action Distribution:** Which action is most popular?
   - Prokuratura vs Donos vs Straż
3. **Completion Rate:** % users who complete full flow (click → modal → send)
   - Target: 60%+
4. **User Retention:** Do memetic actions increase engagement?
   - Measure: Return visits after using action

### Analytics Events:
```javascript
// Track in frontend
gtag('event', 'memetic_action_triggered', {
    'action_type': 'prokuratura',
    'query_id': queryId,
    'completed': true
});
```

---

## 🔒 Security & Privacy

### Important Notes:
1. **NO REAL SENDING:** Always make it ABUNDANTLY clear this is fake
2. **User Data:** Don't store uploaded files (only show preview)
3. **Rate Limiting:** Prevent API abuse
   ```python
   @ratelimit(key='user', rate='10/h', method='POST')
   def generate_prosecutor_letter(request):
       ...
   ```
4. **CSRF Protection:** All POST requests require CSRF token
5. **Logging:** Log actions for monitoring (not for real reporting!)

---

## 🎭 Easter Eggs (Optional)

### Hidden Features:
1. **Konami Code:** Unlock "Wywiad z TVN" action 📺
2. **Special Days:** On April 1st, extra silly responses
3. **Achievement System:** "Donos Master" badge after 10 donosy

---

## 📚 Documentation Updates

**Files to Update:**
1. `docs/USER_GUIDE.md` - Add section "Memiczne Akcje"
2. `docs/ARCHITECTURE_STRUCTURE.md` - Add memetic actions flow
3. `README.md` - Mention fun features

---

## ✅ Definition of Done

Feature is DONE when:
- [ ] All 3 actions (Prokuratura, Donos, Straż) work end-to-end
- [ ] Modals open/close smoothly with animations
- [ ] GPT-5 mini generates contextual content
- [ ] Fake sending animations work perfectly
- [ ] Mobile responsive
- [ ] Unit tests pass (90%+ coverage)
- [ ] E2E tests pass
- [ ] "To był żart 😄" clearly visible everywhere
- [ ] No real emails/calls are sent
- [ ] Documentation updated
- [ ] Code reviewed & merged

---

**Author:** Claude Code + @LaVanguard
**Status:** 📋 Planning Complete - Ready for Implementation
**Next Step:** Review plan → Start implementation → Deploy to staging
