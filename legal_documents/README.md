# Legal Documents Catalog

This directory contains Polish legal documents used for the RAG (Retrieval-Augmented Generation) system.

## Directory Structure

```
legal_documents/
├── raw/                    # Original source PDFs
│   ├── budowa/            # Construction & building law
│   ├── ochrona_przyrody/  # Nature protection law
│   └── przeglady/         # Mandatory inspections
└── processed/             # Preprocessed versions (optional)
```

## Current Documents

### Construction & Building Law (`budowa/`)

| File | Original Name | Pages | Year | Description |
|------|---------------|-------|------|-------------|
| `prawo_budowlane_1994.pdf` | Akt prawny.pdf | 168 | 1994 | Polish Construction Law (Prawo budowlane) - consolidated text |
| `warunki_techniczne_budynki_2022.pdf` | Obwieszczenie Ministra... | ~60 | 2022 | Technical conditions for buildings and their location |
| `warunki_techniczne_metro_2023.pdf` | Techniczny.pdf | 32 | 2023 | Technical conditions for metro construction objects |

### Nature Protection Law (`ochrona_przyrody/`)

*No documents yet*

### Mandatory Inspections (`przeglady/`)

*No documents yet*

## How to Add New Documents

1. Download PDF from official sources:
   - **Primary:** https://isap.sejm.gov.pl/ (Internet System of Legal Acts)
   - **Municipal:** Local government websites
   - **Ministries:** Specific ministry websites

2. Place in appropriate category folder:
   ```bash
   legal_documents/raw/[category]/descriptive_name_year.pdf
   ```

3. Update this README with document metadata

4. Upload via Django admin (http://127.0.0.1:8000/admin/knowledge/document/)

5. Process with management command:
   ```bash
   python manage.py process_documents --all
   ```

## Document Quality Requirements

- **Format:** Text-based PDF (not scanned images)
- **Language:** Polish
- **Length:** 1-200 pages (optimal: 10-50)
- **Encoding:** UTF-8 compatible
- **Source:** Official government/legal sources only

## Preprocessing Status

Current documents contain administrative metadata that may need cleaning:
- ✅ Page headers (Kancelaria Sejmu, Dziennik Ustaw)
- ✅ Document metadata (dates, journal references)
- ✅ Encoding issues (special Polish characters)

Preprocessing will be applied automatically during document processing.

## Git Policy

- **Tracked:** This README and small reference documents (<1 MB)
- **Ignored:** Large PDF files (>1 MB) - see `.gitignore`
- **Reason:** Keep repository size manageable

## Notes

- Documents are sourced from official Polish legal repositories
- All documents are in the public domain (official legal acts)
- For production, consider hosting PDFs externally (S3, etc.)

---

**Last Updated:** 2025-10-12
**Maintained by:** Law Advisor Team
