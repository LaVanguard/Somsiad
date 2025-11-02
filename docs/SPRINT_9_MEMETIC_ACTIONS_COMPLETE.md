# Sprint 9: Memetic Actions - Implementation Complete

**Date**: 2025-11-02
**Status**: ✅ Complete
**Feature**: 3 Interactive Memetic Legal Actions

---

## Overview

Sprint 9 successfully implements 3 humorous but educationally accurate "memetic actions" that users can trigger after receiving AI legal advice. Each action simulates a real-world legal/administrative process with GPT-5-mini generated content, fake animations, and clear "to był żart" disclaimers.

---

## Features Implemented

### 1. ⚖️ Prokuratura (Prosecutor Letter)

**Trigger**: Blue button after AI response
**Flow**:
1. User clicks "⚖️ Prokuratura" button
2. Modal opens with loading spinner
3. GPT-5-mini generates formal "ZAWIADOMIENIE O POPEŁNIENIU PRZESTĘPSTWA"
4. User can edit the letter in textarea
5. User clicks "Wyślij do Prokuratury"
6. Fake e-PUAP sending animation with progress bar:
   - "Łączenie z e-PUAP..."
   - "Weryfikacja dostępu..."
   - "Szyfrowanie dokumentu..."
   - "Wysyłanie do Prokuratury..."
   - "Potwierdzenie dostarczenia..."
7. Success screen with fake reference number (e.g., "PR-3421/2025")
8. Large disclaimer: "😄 To był żart! Nic nie zostało wysłane naprawdę."

**Backend**:
- `MemeticActionsService.generate_prosecutor_letter()`
- GPT-5-mini with temp=0.2 for formal tone
- Fallback template if GPT fails
- Rate limit: 10/h per user

### 2. 📧 Donos do Gminy (Anonymous Complaint Email)

**Trigger**: Orange button after AI response
**Flow**:
1. User clicks "📧 Donos do Gminy" button
2. Modal opens with loading spinner
3. GPT-5-mini generates:
   - Email subject (e.g., "Zgłoszenie nieprawidłowości - budowa bez pozwolenia")
   - Email body (formal complaint to municipal office)
4. User can edit subject and body
5. User can upload files (images/audio/video) as "evidence" (max 5 files, 10MB each)
6. File preview list with remove buttons
7. User clicks "Wyślij Donos"
8. Fake anonymous email sending with progress:
   - "Anonimizacja nadawcy..."
   - "Szyfrowanie załączników..."
   - "Usuwanie metadanych z plików..."
   - "Routing przez TOR..."
   - "Wysyłanie do Urzędu Gminy..."
9. Success screen showing number of attachments
10. Disclaimer: "😄 To był żart! Nic nie zostało wysłane naprawdę."

**Backend**:
- `MemeticActionsService.generate_donos_email()`
- Returns `{subject, body}`
- File handling in frontend only (not actually uploaded)

### 3. 🚔 Straż Miejska (Municipal Guard Call)

**Trigger**: Green button after AI response
**Flow**:
1. User clicks "🚔 Straż Miejska" button
2. Modal opens with calling animation (bouncing phone icon + ping effect)
3. "Dzwonię... 986 - Straż Miejska"
4. After 2-3 seconds, call connects
5. GPT-5-mini generates conversation script (alternating USER/OPERATOR lines)
6. Messages display one by one (2-second intervals) in chat bubbles
7. Call timer runs (00:00 format)
8. Operator info card shows "Dyżurny Straży Miejskiej" with pulsing green dot
9. User can click "Rozłącz" to end call
10. Success screen: "✅ Patrol wysłany! Czas przybycia: ~15 minut"
11. Shows total call duration
12. Disclaimer: "😄 To był żart! Nie dzwoniliśmy naprawdę. To symulacja."

**Backend**:
- `MemeticActionsService.generate_straz_call_script()`
- Returns array of `{id, sender, text}` messages
- Parses "USER:" and "OPERATOR:" prefixes from GPT response

---

## Technical Implementation

### Backend

**File**: `knowledge/services/memetic_actions_service.py`
- `MemeticActionsService` class
- 3 generation methods (prosecutor, donos, straz)
- GPT-5-mini with temperature=0.2 (formal tone)
- Fallback templates for each action
- Polish date formatting helper

**File**: `accounts/memetic_views.py`
- 3 API endpoints:
  - `POST /api/actions/prosecutor/generate/`
  - `POST /api/actions/donos/generate/`
  - `POST /api/actions/straz/call/`
- `@login_required` + `@ratelimit(10/h)` on all endpoints
- Returns JSON with generated content + timestamp

**File**: `config/urls.py`
- Added 3 new URL routes

### Frontend

**File**: `templates/home.html`
- Added Alpine.js state (285 lines of new code):
  - Prosecutor: `showProsecutorModal`, `generatingLetter`, `prosecutorLetter`, `sendingLetter`, etc.
  - Donos: `showDonosModal`, `donosSubject`, `donosBody`, `donosFiles`, etc.
  - Straż: `showStrazModal`, `callConnected`, `callMessages`, `callTimer`, etc.
- Alpine.js methods:
  - `generateProsecutorLetter(question, answer)`
  - `sendProsecutorLetter()` - fake sending animation
  - `resetProsecutorModal()`
  - `generateDonosEmail(question, answer)`
  - `handleDonosFiles(event)` - file upload handling
  - `removeDonosFile(index)`
  - `sendDonosEmail()` - fake sending with progress
  - `resetDonosModal()`
  - `startStrazCall(question, answer)` - call simulation
  - `endCall()`
  - `resetStrazModal()`
- Included 3 modal partials at end of template

**File**: `templates/partials/prosecutor_modal.html` (114 lines)
- Full modal with 4 states: generating → editing → sending → success
- Editable textarea for letter content
- Fake e-PUAP sending animation with progress bar

**File**: `templates/partials/donos_modal.html` (138 lines)
- Email subject/body editing
- Drag-drop file upload zone
- File preview list with icons (📷🎥🎵📎)
- File size formatter
- Fake anonymous sending animation

**File**: `templates/partials/straz_modal.html` (116 lines)
- Ringing animation (bouncing phone icon)
- Call connected state with operator card
- Chat-style message bubbles (user vs operator)
- Call timer with interval
- Hang up button
- Success with patrol ETA

**File**: `templates/partials/message.html`
- Updated 3 action buttons:
  - Changed from HTMX `hx-post` to Alpine.js `@click`
  - Color-coded: blue (Prokuratura), orange (Donos), green (Straż)
  - Added emojis to button labels
  - Passes `question` and `answer` to Alpine.js methods

### Tests

**File**: `tests/test_memetic_actions.py` (293 lines)
- **17 unit tests total**:
  - 7 service tests (TestMemeticActionsService)
  - 10 view tests (TestMemeticActionsViews)
- Tests GPT-5-mini success and fallback scenarios
- Tests authentication, rate limiting, HTTP methods
- Mock-based testing for LLM calls

---

## File Changes Summary

### Created Files (6)
1. `knowledge/services/memetic_actions_service.py` - 336 lines
2. `accounts/memetic_views.py` - 135 lines
3. `templates/partials/prosecutor_modal.html` - 114 lines
4. `templates/partials/donos_modal.html` - 138 lines
5. `templates/partials/straz_modal.html` - 116 lines
6. `tests/test_memetic_actions.py` - 293 lines

### Modified Files (3)
1. `templates/home.html` - Added 285 lines of Alpine.js state/methods
2. `templates/partials/message.html` - Updated 3 action buttons (42 lines changed)
3. `config/urls.py` - Added 3 new URL routes (5 lines added)

### Total Lines of Code Added
- **Backend**: 471 lines
- **Frontend**: 653 lines
- **Tests**: 293 lines
- **Total**: ~1,417 lines of new code

---

## API Endpoints

### 1. Generate Prosecutor Letter
```
POST /api/actions/prosecutor/generate/
Content-Type: application/json
Authorization: Required (login_required)

Request:
{
  "question": "Sąsiad buduje garaż bez pozwolenia",
  "ai_answer": "Budowa bez pozwolenia jest wykroczeniem..."
}

Response:
{
  "letter": "Do Prokuratury Rejonowej...",
  "generated_by": "gpt-5-mini",
  "timestamp": "2025-11-02T14:30:00"
}
```

### 2. Generate Donos Email
```
POST /api/actions/donos/generate/
Content-Type: application/json
Authorization: Required

Request:
{
  "question": "Dzikie wysypisko śmieci",
  "ai_answer": "Należy zgłosić to do gminy..."
}

Response:
{
  "subject": "Zgłoszenie nieprawidłowości - dzikie wysypisko",
  "body": "Szanowni Państwo...",
  "generated_by": "gpt-5-mini",
  "timestamp": "2025-11-02T14:31:00"
}
```

### 3. Generate Straż Call Script
```
POST /api/actions/straz/call/
Content-Type: application/json
Authorization: Required

Request:
{
  "question": "Głośna muzyka o 2 w nocy",
  "ai_answer": "To może być wykroczenie..."
}

Response:
{
  "messages": [
    {"id": 1, "sender": "operator", "text": "Straż Miejska, słucham"},
    {"id": 2, "sender": "user", "text": "Dzwonię zgłosić głośną muzykę..."},
    ...
  ],
  "patrol_time": "10-15 minut",
  "generated_by": "gpt-5-mini",
  "timestamp": "2025-11-02T14:32:00"
}
```

---

## Security & Rate Limiting

- **Authentication**: All endpoints require `@login_required`
- **Rate Limiting**: `@ratelimit(key='user', rate='10/h', method='POST', block=True)`
- **Input Validation**: Question parameter required (400 error if missing)
- **HTTP Methods**: Only POST allowed (405 error for GET/etc.)
- **CSRF Protection**: All POST requests require CSRF token

---

## Error Handling

### GPT-5-mini Failures
If GPT-5-mini API fails, each action has a fallback template:
- **Prosecutor**: Generic ZAWIADOMIENIE template with user's question
- **Donos**: Generic complaint email template
- **Straż**: 6-message conversation template
- All fallbacks marked with `"generated_by": "template"`

### Frontend Errors
- Fetch errors display "Błąd generowania..." in modal
- Console.error() logs for debugging
- Modal allows retry (user can close and click button again)

---

## User Experience

### Humor Elements
- **Fake Progress Bars**: "Routing przez TOR...", "Szyfrowanie załączników..."
- **Fake Reference Numbers**: "PR-3421/2025"
- **Realistic Animations**: Bouncing phone icon, pulsing "Na linii" dot, progress bars
- **Polish Bureaucracy Parody**: Formal language, e-PUAP references, article citations

### Educational Value
- **Accurate Legal Content**: GPT-5-mini generates real prosecutor letter format
- **Proper Procedures**: Shows how formal complaints are structured
- **Legal Citations**: Includes real article numbers (e.g., "art. 304 § 2 KPK")
- **Clear Disclaimers**: Every action ends with "😄 To był żart!"

### Accessibility
- **Keyboard Navigation**: Escape key closes modals
- **Screen Readers**: Semantic HTML (buttons, labels, headers)
- **Mobile Responsive**: Modals scale to screen size (max-w-3xl with p-4 padding)

---

## Performance

### Backend
- **GPT-5-mini Speed**: ~2-5 seconds for letter generation
- **Fallback Speed**: Instant (<100ms) if GPT fails
- **Rate Limiting**: Prevents abuse (10 requests/hour per user)

### Frontend
- **Modal Loading**: Instant (Alpine.js reactivity)
- **Animations**: CSS transitions (smooth 60fps)
- **File Handling**: Client-side only (no upload, instant preview)
- **Memory**: Call timer cleanup with `clearInterval()`

---

## Testing

### Unit Tests (17 total)
✅ Service initialization
✅ GPT-5-mini success scenarios (3 actions)
✅ Fallback template scenarios (3 actions)
✅ API endpoint success (3 actions)
✅ Authentication required (3 actions)
✅ HTTP method restrictions (3 actions)
✅ Input validation

### Django System Check
✅ `python manage.py check` - No issues (3 silenced)

### Manual E2E Testing Checklist
- [ ] Login as user
- [ ] Ask a legal question
- [ ] Click each action button (Prokuratura, Donos, Straż)
- [ ] Verify GPT-5-mini generation
- [ ] Edit generated content
- [ ] Test file upload (Donos)
- [ ] Trigger fake sending animations
- [ ] Verify disclaimers appear
- [ ] Test modal close/reset
- [ ] Verify rate limiting (11th request in 1 hour should fail)

---

## Configuration

### Model Settings
```python
# config/settings/base.py
RAG_CONFIG = {
    'GENERATION_MODEL': 'gpt-5-mini',  # Used for memetic actions
    'TEMPERATURE': 0.3,
}

# knowledge/services/memetic_actions_service.py
self.llm = ChatOpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    model="gpt-5-mini",
    temperature=0.2  # Lower temp for formal tone
)
```

### Rate Limiting
```python
# accounts/memetic_views.py
@ratelimit(key='user', rate='10/h', method='POST', block=True)
```

---

## Future Enhancements (Not in Scope)

1. **Real Integration**: Actually send emails/letters (with user consent)
2. **Email Templates**: Save generated letters as PDFs
3. **Conversation History**: Store Straż call scripts in database
4. **More Actions**: "Rzecznik Praw Obywatelskich", "Media Contact"
5. **Translations**: English version for international users
6. **Analytics**: Track which actions are most popular

---

## Known Limitations

1. **File Upload**: Files are not actually uploaded (displayed only)
2. **Call Simulation**: No real audio/phone connection
3. **Reference Numbers**: Randomly generated (not tracked)
4. **Rate Limit**: 10/hour may be too restrictive for demo purposes
5. **GPT Failures**: If OpenAI API is down, fallback templates are less personalized

---

## Deployment Notes

### Environment Variables Required
```env
OPENAI_API_KEY=sk-...
```

### Static Files
No new static files added (uses existing Tailwind CSS + Alpine.js)

### Database Migrations
No database changes (no new models)

### Dependencies
No new Python packages required (langchain-openai already installed)

---

## Sprint Metrics

- **Duration**: 1 session (2025-11-02)
- **Lines of Code**: 1,417 new lines
- **Files Created**: 6
- **Files Modified**: 3
- **Tests Written**: 17
- **API Endpoints Added**: 3
- **Modals Created**: 3
- **Features Delivered**: 3/3 ✅

---

## Conclusion

Sprint 9 successfully delivers all 3 memetic legal actions with:
- ✅ GPT-5-mini powered content generation
- ✅ Realistic UI/UX with fake animations
- ✅ Clear educational disclaimers
- ✅ Full frontend/backend integration
- ✅ Comprehensive unit tests
- ✅ Rate limiting and security
- ✅ Mobile-responsive design

The feature is **ready for production** after manual E2E testing and user acceptance.

---

**Implementation Status**: ✅ COMPLETE
**Next Steps**: Manual E2E testing → Deploy to production → User feedback

---

*Generated by Claude Code - 2025-11-02*
