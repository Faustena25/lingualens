import re

try:
    import emoji
except ImportError:
    raise SystemExit("Run: pip install emoji")

from lingualens_core import predict_sentiment

GREETINGS = {"hi", "hii", "hiii", "hello", "hey", "hlo", "helo", "vanakkam",
             "namaste", "namaskaram", "hai", "yo", "sup"}

# Emojis that can mean either happy or sad tears -> never force a polarity
AMBIGUOUS_EMOJI = {"😭", "🥲", "😿"}
_IGNORE = {"\u200d", "\ufe0f"}

# Romanized slang -> plain English the model understands.
# Matched AFTER letter-stretching is collapsed (aaaa -> aa). Order matters.
_GLOSS = [
    # ---- Tanglish ----
    (r"\bthanga\s+mudiyal\w*", "cannot bear it"),
    (r"\bmudiyal\w*",          "cannot do it"),
    (r"\b(?:ai|a)+y+o+\b",     "oh no"),
    (r"\bkashtam\b",           "terrible suffering"),
    (r"\bmokk?a\w*\b",         "boring, worthless"),
    (r"\bpidikal\w*",          "do not like it"),
    (r"\bsemma\b",             "awesome"),
    (r"\bvera\s+level\b",      "next level awesome"),
    # ---- Hinglish ----
    (r"\bbakw+a+s\b",          "nonsense, terrible"),
    (r"\bbek[ai]+r\b",         "useless"),
    (r"\bghatiya\b",           "worst quality"),
    (r"\bpasand\s+nahi\w*",    "do not like"),
    (r"\bzabardast\b",         "excellent"),
    (r"\bkamaal\b",            "amazing"),
    (r"\bbehtareen\b",         "excellent"),
    (r"\bmast\b",              "awesome"),
    # ---- Manglish ----
    (r"\bad+i+p+o+l+i+\b|\bpoli\b|\bpwoli\b", "awesome"),
    (r"\bkidilam\b|\bkidu\b",  "awesome"),
    (r"\bmosham\b",            "terrible"),
    (r"\bishtamalla\w*",       "did not like it"),
    (r"\bishtam\w*",           "liked it"),
    (r"\bkollam\b",            "good"),
]


def normalize(text: str) -> str:
    """Collapse stretched letters, then gloss common slang to English."""
    t = re.sub(r"([^\W\d_])\1{2,}", r"\1\1", text)   # aaaa -> aa (letters only)
    for pat, rep in _GLOSS:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    return t


def prepare_text(text: str) -> str:
    """Emoji -> plain words, e.g. '💯 suppar' -> 'hundred points suppar'."""
    t = emoji.demojize(text, delimiters=(":", ":"))
    t = re.sub(r"(:[^\s:]+:)(\s*\1)+", r"\1", t)  # collapse repeated emojis
    t = re.sub(r":([^\s:]+):", lambda m: " " + m.group(1).replace("_", " ").replace("-", " ") + " ", t)
    return re.sub(r"\s+", " ", t).strip()


def predict_with_emoji(text: str) -> dict:
    clean = prepare_text(normalize(text))
    words = re.findall(r"\w+", clean.lower())

    # greeting-only text has no sentiment
    if words and all(w in GREETINGS for w in words):
        return {"label": "Neutral",
                "scores": {"Negative": 0.0, "Neutral": 1.0, "Positive": 0.0},
                "source": "rule", "prepared": clean}

    r = predict_sentiment(clean or text)
    if isinstance(r, list):
        r = r[0]
    out = {"label": r["label"], "scores": r["scores"],
           "source": "model", "prepared": clean}

    # crying / laughing-tears emojis alone are ambiguous
    chars = [c for c in text if not c.isspace() and c not in _IGNORE]
    if chars and all(c in AMBIGUOUS_EMOJI for c in chars):
        out["label"] = "Uncertain"
        out["source"] = "rule"
    return out