# Sample Legal Documents for Testing

This directory contains sample legal texts for testing the RAG system.

## Usage

These are simplified legal texts for **testing purposes only**. They are not comprehensive legal documents!

### For Testing:

1. Convert these `.txt` files to PDF format
2. Upload via Django admin: `http://127.0.0.1:8000/admin/knowledge/document/`
3. Process: `python manage.py process_documents --all`
4. Test queries in chat interface

### Converting to PDF:

**Online (easiest):**
- Use: https://txt2pdf.com or similar

**Command line (Windows):**
```powershell
# Using Microsoft Word (if installed)
# Just open .txt and "Save As PDF"
```

**Python script:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def txt_to_pdf(txt_file, pdf_file):
    c = canvas.Canvas(pdf_file, pagesize=letter)
    with open(txt_file, 'r', encoding='utf-8') as f:
        text = f.read()

    y = 750
    for line in text.split('\n'):
        c.drawString(50, y, line[:80])  # Wrap long lines
        y -= 15
        if y < 50:
            c.showPage()
            y = 750
    c.save()

# Usage
txt_to_pdf('budowa_przegrod.txt', 'budowa_przegrod.pdf')
```

---

**Note:** These are mock documents for demonstration. Real legal advice requires consulting actual legal texts and professionals.
