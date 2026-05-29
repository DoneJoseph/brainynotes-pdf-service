# BrainyNotes AI — PDF Microservice

Flask API that generates branded study PDFs from structured JSON.
Deployed on Railway. Called by Supabase Edge Functions.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

## Test the API

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "course": {
      "code": "KU4VACCOM101",
      "semester": "Semester 4",
      "note_type": "SHORT NOTES",
      "subject": "Consumer Rights and Protection",
      "module": "Module 1",
      "title1": "Fundamentals of",
      "title2": "Consumer Rights",
      "program": "BCom",
      "credits": "3 Credits"
    },
    "sections": [
      {
        "h1": "Consumer",
        "body": "A consumer is a person who buys goods or avails services for personal use.",
        "definition": "Consumer means any person who buys goods for consideration.",
        "numbered_list": [
          {"title": "Right to Safety", "desc": "Protected from hazardous goods."},
          {"title": "Right to Choose", "desc": "Access variety at competitive prices."}
        ],
        "recall_items": [
          {"keyword": "Consumer", "desc": "Buys for personal use, not resale."}
        ],
        "subsections": []
      }
    ]
  }' --output test_output.pdf
```

## Deploy to Railway

1. Push this folder to a GitHub repo
2. Go to railway.app → New Project → Deploy from GitHub
3. Select the repo
4. Railway auto-detects Python + Procfile
5. Copy the generated URL → paste into Lovable as PDF_SERVICE_URL

## Folder Structure

```
pdf-service/
├── app.py              ← Flask API
├── pdf_generator.py    ← ReportLab PDF engine
├── requirements.txt
├── Procfile
├── railway.json
├── fonts/
│   ├── Inter-Regular.ttf
│   ├── Inter-Bold.ttf
│   └── Inter-Italic.ttf
└── static/
    ├── brainynotes-logo-light.png
    ├── brainynotes-logo-dark.png
    └── qr_brainynotes.png
```
