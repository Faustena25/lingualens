import re

try:
    import emoji
except ImportError:
    raise SystemExit("Run: pip install emoji")

from lingualens_core import predict_sentiment

CONF_MIN = 0.65  # same threshold app.py uses for "Uncertain"

GREETINGS = {"hi", "hii", "hiii", "hello", "hey", "hlo", "helo", "vanakkam",
             "namaste", "namaskaram", "hai", "yo", "sup"}

AMBIGUOUS_EMOJI = {"😭", "😢", "🥲", "😿"}
POSITIVE_EMOJI = set("❤🤍💙💚💛🧡💜🩷🩵🩶🤎💖💕💗💓💞💝💘😍🥰😘😻🤩🥳👏😂🤣🙌🔥💯👍👌")
_IGNORE = {"‍", "️"}

# "Anyone in 2026?" / "who is watching in July" -> check-in, no sentiment
CHECKIN = re.compile(
    r"\b(anyone|anybody|who(?:'s| is)?|any\s+one)\b.{0,25}\b(in|from|watching|listening|here)\b.{0,25}\b(19|20)\d\d\b"
    r"|\b(19|20)\d\d\b.{0,15}\b(anyone|anybody|here|watching|listening)\b"
    r"|\b(anyone|anybody)\s+(here|watching|listening)\b",
    re.IGNORECASE,
)
# if any of these appear, the comment has real sentiment -> let the model decide
SENTIMENT_HINTS = {"love", "loved", "best", "super", "superb", "awesome", "amazing",
                   "great", "beautiful", "nice", "good", "fantastic", "masterpiece",
                   "hate", "worst", "terrible", "bad", "boring", "useless"}

# words used by the lexicon safety net (checked on the glossed English text)
POS_WORDS = {"good", "great", "awesome", "amazing", "excellent", "perfect", "love",
             "loved", "best", "super", "superb", "nice", "worth", "fantastic",
             "beautiful", "wonderful", "brilliant", "masterpiece", "liked"}
NEG_WORDS = {"bad", "worst", "terrible", "useless", "waste", "boring", "nonsense",
             "poor", "awful", "pathetic", "worthless", "hate", "disappointed"}
NEGATIONS = {"not", "no", "never", "dont", "don", "didnt", "didn", "cannot", "cant",
             "isnt", "wasnt", "nothing"}

# Order matters: longer / more specific patterns first.
_GLOSS = [
    # ---- Tanglish ----
    (r"\bthanga\s+mudiyal\w*", "cannot bear it, terrible"),
    (r"\bmudiyal\w*",          "cannot do it, terrible"),
    (r"\b(?:ai|a)+y+o+\b",     "oh no, terrible"),
    (r"\bkashtam\b",           "terrible suffering"),
    (r"\bmokk?a\w*\b",         "boring, worthless"),
    (r"\bpidikal\w*",          "do not like it"),
    (r"\bsemma\b",             "awesome"),
    (r"\bvera\s+level\b",      "next level awesome"),
    (r"\bkuzhappam\s+illa\w*", "fine, good"),
    (r"\bkuzhappam\b",         "problem"),
    (r"\bnalla\w*",            "good"),
    # ---- Hinglish ----
    (r"\bbakw+a+s\b",          "nonsense, terrible"),
    (r"\bbek[ai]+r\b",         "useless"),
    (r"\bghatiya\b",           "worst quality"),
    (r"\bkharab\b",            "bad"),
    (r"\bpasand\s+nahi\w*",    "do not like"),
    (r"\bzabardast\b",         "excellent"),
    (r"\bkamaal\b",            "amazing"),
    (r"\bbehtareen\b",         "excellent"),
    (r"\bbadh?iya\b",          "great"),
    (r"\bbilkul\s+perfect\b",  "absolutely perfect"),
    (r"\b(?:lene\s+|khareedne\s+)?layak\b", "worth buying"),
    (r"\bmast\b",              "awesome"),
    (r"\bacch?[aei]+\b",       "good"),
    # ---- Manglish ----
    (r"\bpaisa\s+vasool\b|\bvasool\b", "worth the money, great"),
    (r"\bad+i+p+o+l+i+\b|\bpoli\b|\bpwoli\b", "awesome"),
    (r"\bkidilam\b|\bkidu\b",  "awesome"),
    (r"\bnannayi\w*",          "good"),
    (r"\bvalare\b",            "very"),
    (r"\bsh?eriyalla\b|\bsariyalla\b|\bsariyilla\b", "is not right, bad"),
    (r"\bmosham\b",            "terrible"),
    (r"\bishtamalla\w*",       "did not like it"),
    (r"\bishtapett\w*|\bishtam\w*", "liked it"),
    (r"\bkollam\b",            "good"),
]


def normalize(text: str) -> str:
    """Collapse stretched letters, gloss slang to English, keep one 'terrible'."""
    t = re.sub(r"([^\W\d_])\1{2,}", r"\1\1", text)
    for pat, rep in _GLOSS:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    parts = t.split("terrible")
    if len(parts) > 2:
        t = "".join(parts[:-1]) + "terrible" + parts[-1]
    return t


def prepare_text(text: str) -> str:
    """Emoji -> plain words, e.g. '💯 suppar' -> 'hundred points suppar'."""
    t = emoji.demojize(text, delimiters=(":", ":"))
    t = re.sub(r"(:[^\s:]+:)(\s*\1)+", r"\1", t)
    t = re.sub(r":([^\s:]+):", lambda m: " " + m.group(1).replace("_", " ").replace("-", " ") + " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _rule(label: str, clean: str) -> dict:
    s = {"Negative": 0.0, "Neutral": 0.0, "Positive": 0.0}
    s[label] = 1.0
    return {"label": label, "scores": s, "source": "rule", "prepared": clean}


def _lexicon(words, chars):
    """Return (pos_hits, neg_hits, has_negation) for the glossed text."""
    pos = sum(w in POS_WORDS for w in words) + sum(c in POSITIVE_EMOJI for c in chars)
    neg = sum(w in NEG_WORDS for w in words)
    return pos, neg, bool(set(words) & NEGATIONS)


def predict_with_emoji(text: str) -> dict:
    clean = prepare_text(normalize(text))
    words = re.findall(r"\w+", clean.lower())
    chars = [c for c in text if not c.isspace() and c not in _IGNORE]

    # greeting-only text has no sentiment
    if words and all(w in GREETINGS for w in words):
        return _rule("Neutral", clean)

    # check-in comments ("Anyone in 2026?") are Neutral unless real sentiment words appear
    if CHECKIN.search(clean) and not (set(words) & SENTIMENT_HINTS):
        return _rule("Neutral", clean)

    # hearts / love / celebration emojis alone are Positive
    if chars and all(c in POSITIVE_EMOJI for c in chars):
        return _rule("Positive", clean)

    r = predict_sentiment(clean or text)
    if isinstance(r, list):
        r = r[0]
    out = {"label": r["label"], "scores": r["scores"],
           "source": "model", "prepared": clean}

    # crying / laughing-tears emojis alone are ambiguous
    if chars and all(c in AMBIGUOUS_EMOJI for c in chars):
        out["label"] = "Uncertain"
        out["source"] = "rule"
        return out

    # lexicon safety net: only for clear one-sided comments with no negation
    pos, neg, negated = _lexicon(words, chars)
    if not negated and (pos == 0) != (neg == 0):
        lex = "Positive" if pos else "Negative"
        hits = pos or neg
        conf = max(r["scores"].values())
        if lex != r["label"] and (conf < CONF_MIN or hits >= 2):
            return _rule(lex, clean)

    return out