import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lingualens_final")

tok = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR).eval()
id2label = {int(k): v.capitalize() for k, v in model.config.id2label.items()}
names = [id2label[i] for i in range(len(id2label))]


def _probs(texts):
    texts = [str(t) for t in texts]
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        return torch.softmax(model(**enc).logits, dim=-1)


def predict_sentiment(texts):
    if isinstance(texts, str):
        texts = [texts]
    out = []
    for p in _probs(texts):
        out.append({
            "label": id2label[int(p.argmax())],
            "scores": {id2label[i]: round(float(p[i]), 3) for i in range(len(p))},
        })
    return out


_explainer = None


def _get_explainer():
    global _explainer
    if _explainer is None:
        import shap
        f = lambda t: _probs(t).numpy()
        _explainer = shap.Explainer(f, shap.maskers.Text(tok), output_names=names)
    return _explainer


def _word_attributions(sv_i, pred):
    vals = sv_i.values[:, pred]
    toks = list(sv_i.data)
    words, cur, cur_val = [], "", 0.0
    for k, (t, v) in enumerate(zip(toks, vals)):
        cur += t.strip()
        cur_val += v
        if t.endswith(" ") or k == len(toks) - 1:
            if cur:
                words.append((cur, cur_val))
            cur, cur_val = "", 0.0
    return sorted(words, key=lambda x: -abs(x[1]))


def explain_text(text, top_k=6, max_evals=600):
    info = predict_sentiment(text)[0]
    pred = names.index(info["label"])
    sv_i = _get_explainer()([text], max_evals=max_evals)[0]
    words = _word_attributions(sv_i, pred)[:top_k]
    return {
        "label": info["label"],
        "scores": info["scores"],
        "top_words": [{"word": w, "score": round(float(v), 3)} for w, v in words],
    }
