import re
import unicodedata

import emoji
from indic_transliteration import sanscript

from lingualens_core import predict_sentiment

POS = set("😀😁😂🤣😃😄😅😆😊😍🥰😘😻😎🤩🥳😇🤗😌👍👏🙌💪🔥💯❤♥💕💖💗💙💚💛💜🧡🤍✨🎉🙏")
NEG = set("😡😠🤬😞😢😤👎💔🤮🤢😒🙄😑😖😫😩😔😟😕🖕💩😾")
SKIP = re.compile("[\ufe0f\u200d\U0001F3FB-\U0001F3FF]")
URL = re.compile(r"https?://\S+|www\.\S+")
HANDLE = re.compile(r"@\w+")

SCRIPTS = [
    (0x0D00, 0x0D7F, sanscript.MALAYALAM),
    (0x0B80, 0x0BFF, sanscript.TAMIL),
    (0x0900, 0x097F, sanscript.DEVANAGARI),
    (0x0C00, 0x0C7F, sanscript.TELUGU),
]

# praise idioms built on a negation ("no other song like this")
IDIOMS = re.compile(
    r"ഇതുപോല.*(ഇല്ല|വില്ല|കില്ല)"
    r"|இது ?போல.*இல்லை|இதை ?விட.*இல்லை"
    r"|\b(ithu ?pol\w*|idhu ?pol\w*|itupol\w*)\b.*\b(illa\w*|illai|undavilla|untavilla|undakilla|undaavilla)\b"
    r"|\b(jaisa|jaise)\b.*\bkoi\b.*\bnahi\w*\b",
    re.IGNORECASE,
)


def strip_marks(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def romanize(text):
    for lo, hi, scheme in SCRIPTS:
        if any(lo <= ord(ch) <= hi for ch in text):
            try:
                out = sanscript.transliterate(text, scheme, sanscript.ITRANS)
                return strip_marks(out).lower()
            except Exception:
                return text
    return text


def predict_with_emoji(text):
    text = HANDLE.sub(" ", URL.sub(" ", text))
    text = SKIP.sub("", text)

    found = [e["emoji"] for e in emoji.emoji_list(text)]
    net = sum(e in POS for e in found) - sum(e in NEG for e in found)

    stripped = emoji.replace_emoji(text, " ")
    stripped = re.sub(r"\s+", " ", stripped).strip()
    has_words = re.search(r"[^\W\d_]", stripped) is not None

    # emoji-only comment: rule-based
    if not has_words:
        if net > 0:
            s = {"Negative": 0.05, "Neutral": 0.05, "Positive": 0.90}
        elif net < 0:
            s = {"Negative": 0.90, "Neutral": 0.05, "Positive": 0.05}
        else:
            s = {"Negative": 0.10, "Neutral": 0.80, "Positive": 0.10}
        return {"label": max(s, key=s.get), "scores": s, "source": "emoji-rule"}

    roman = romanize(stripped)

    # negated-praise idioms
    if IDIOMS.search(stripped) or IDIOMS.search(roman):
        s = {"Negative": 0.05, "Neutral": 0.05, "Positive": 0.90}
        return {"label": "Positive", "scores": s, "source": "idiom-rule"}

    # model on romanized text, nudged by emoji sentiment
    res = predict_sentiment(roman)[0]
    s = dict(res["scores"])
    if net != 0:
        w = min(0.15 * abs(net), 0.30)
        s["Positive" if net > 0 else "Negative"] += w
        total = sum(s.values())
        s = {k: round(v / total, 3) for k, v in s.items()}
    return {"label": max(s, key=s.get), "scores": s,
            "source": "model+emoji" if net != 0 else "model"}