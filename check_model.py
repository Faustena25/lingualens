import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 1) EDIT THIS: folder that contains config.json + model.safetensors
MODEL_PATH = r"lingualens_final"

tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).eval()
print("id2label:", model.config.id2label, "\n")

tests = {
    "Tanglish": ["Intha padam semma mass da!", "Padam mokka, waste of time", "Climax kollam but first half bore"],
    "Hinglish": ["Ye movie bakwaas thi, paisa waste", "Kya zabardast acting hai yaar, loved it!", "Movie theek thi, na acchi na buri"],
    "Manglish": ["Adipoli padam, nalla acting", "Ee padam valare mosham aayirunnu"],
}

print("=== RAW MODEL ===")
for lang, sents in tests.items():
    for t in sents:
        x = tok(t, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            p = torch.softmax(model(**x).logits, dim=-1)[0]
        top = model.config.id2label[int(p.argmax())]
        print(f"[{lang}] {t}\n   -> {top}  {[round(v, 3) for v in p.tolist()]}")

print("\n=== YOUR predict_sentiment() ===")
try:
    from lingualens_core import predict_sentiment
    for lang, sents in tests.items():
        for t in sents:
            print(f"[{lang}] {t}\n   -> {predict_sentiment(t)}")
except Exception as e:
    print("Could not run predict_sentiment:", e)
