-- One row per "Analyse" run (a YouTube video or an uploaded CSV)
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,           -- 'youtube' or 'csv'
    source_label TEXT NOT NULL,          -- video title / filename, shown in History
    source_ref TEXT,                     -- YouTube URL or original filename
    created_at TEXT NOT NULL,            -- ISO timestamp

    total_comments INTEGER NOT NULL,
    overall_sentiment TEXT NOT NULL,     -- 'Positive' | 'Negative' | 'Neutral'
    overall_confidence REAL NOT NULL,    -- 0.0 - 1.0
    dominant_language TEXT NOT NULL,     -- 'Tanglish' | 'Hinglish' | 'Tenglish' | 'Manglish' | 'English'
    top_emotion TEXT NOT NULL,           -- 'Joy' | 'Anger' | 'Sadness' | 'Fear' | 'Surprise'

    sentiment_positive_pct REAL NOT NULL,
    sentiment_negative_pct REAL NOT NULL,
    sentiment_neutral_pct REAL NOT NULL,

    emotion_joy_pct REAL NOT NULL,
    emotion_anger_pct REAL NOT NULL,
    emotion_sadness_pct REAL NOT NULL,
    emotion_fear_pct REAL NOT NULL,
    emotion_surprise_pct REAL NOT NULL,

    lang_tanglish_pct REAL NOT NULL,
    lang_hinglish_pct REAL NOT NULL,
    lang_tenglish_pct REAL NOT NULL,
    lang_manglish_pct REAL NOT NULL,
    lang_english_pct REAL NOT NULL,

    bias_gap_pct REAL NOT NULL,          -- max F1 gap across language groups
    bias_flag INTEGER NOT NULL           -- 1 if gap > 10%, else 0
);

-- One row per comment belonging to an analysis
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    sentiment TEXT NOT NULL,             -- 'Positive' | 'Negative' | 'Neutral'
    confidence REAL NOT NULL,
    emotion TEXT NOT NULL,
    language TEXT NOT NULL,
    shap_tokens TEXT,                    -- JSON string: [{"token": "worst", "score": -0.82}, ...]
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);

-- F1 score per language group, per analysis (for the Bias Audit table)
CREATE TABLE IF NOT EXISTS bias_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    language TEXT NOT NULL,              -- 'Tamil' | 'Hindi' | 'Telugu' | 'Malayalam'
    f1_score REAL NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);
