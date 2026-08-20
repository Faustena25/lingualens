# LinguaLens — Prototype

Explainable and bias-aware sentiment analysis for Indian code-switched text
(Tanglish, Hinglish, Tenglish, Manglish), built from the SRS and System
Design deck.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000, then either:
- Upload `static/sample_comments.csv` (or your own CSV with a `comment`/`review`/`text` column), or
- Paste a YouTube URL (demo mode — see note below).

## What's real vs. stubbed, and why

| Component | Status | Notes |
|---|---|---|
| Flask app, routes, CSV upload | ✅ Real | Full FR1 flow for CSV |
| Preprocessing (FR2) | ✅ Real | Emoji→text, URL/@/# stripping |
| Language ID (FR2) | ✅ Real | Lexicon-tag based, not a trained classifier |
| Sentiment + confidence (FR3) | ⚠️ Lexicon-based | Stands in for fine-tuned XLM-RoBERTa — no GPU/HuggingFace access in this sandbox |
| Emotion detection (FR4) | ⚠️ Lexicon-based | Stands in for distilroberta-base |
| Word-level explainability (FR4) | ⚠️ Approximated | Per-token lexicon scores highlighted like SHAP output; not real SHAP values (those need an actual trained model) |
| Bias audit (FR5) | ⚠️ Proxy metric | Uses avg. confidence per language group instead of per-group F1, since F1 needs gold labels the live inference data doesn't have |
| SQLite history/persistence (FR5) | ✅ Real | Full CRUD, matches the ERD in the design deck |
| Dashboard + CSV export (FR5) | ✅ Real | Chart.js donut/radar/bar, all working |
| YouTube Data API fetching (FR1) | ⚠️ Stubbed | Returns a labelled demo comment set. Live fetching needs a server-side `YOUTUBE_API_KEY` env var — see `app.py::_demo_youtube_comments` for the swap-in point |

## Upgrading to the real models

1. **Sentiment/emotion**: replace the body of `analyze_comment()` in
   `models/nlp_engine.py` with a call to your fine-tuned XLM-RoBERTa /
   distilroberta-base checkpoints (e.g. via `transformers.pipeline`). Keep
   the same return dict shape and nothing else in the app needs to change.
2. **Explainability**: once a real model is in place, swap the lexicon
   attribution loop for actual `shap.Explainer` token attributions.
3. **Bias audit**: once you have a labelled validation set per language,
   replace the confidence-gap proxy in `models/bias_audit.py` with a real
   per-language F1 computation.
4. **YouTube**: set `YOUTUBE_API_KEY` as an environment variable and
   replace `_demo_youtube_comments()` in `app.py` with a real
   `googleapiclient.discovery.build("youtube","v3")` call to
   `commentThreads().list()`.

## Project layout

```
lingualens/
├── app.py                  # Flask routes
├── models/
│   ├── lexicon.py          # multilingual sentiment/emotion word lexicon
│   ├── nlp_engine.py        # FR2/FR3/FR4 pipeline
│   └── bias_audit.py        # FR5 fairness audit
├── database/
│   ├── schema.sql
│   └── db.py
├── templates/               # Jinja2 + Bootstrap 5 + Chart.js
├── static/
│   ├── css/style.css
│   └── sample_comments.csv
└── requirements.txt
```
