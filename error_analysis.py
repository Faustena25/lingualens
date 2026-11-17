"""LinguaLens error analysis.
Usage: python error_analysis.py [val_predictions.csv] [--train train.csv]
"""
import sys
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

args = sys.argv[1:]
train_path = None
if "--train" in args:
    i = args.index("--train")
    train_path = args[i + 1]
    del args[i:i + 2]
path = args[0] if args else "data/val_predictions.csv"

df = pd.read_csv(path)
print("Columns:", list(df.columns))


def pick(cands):
    for c in cands:
        if c in df.columns:
            return c
    return None


TEXT = pick(["text", "clean_text", "sentence", "comment"])
TRUE = pick(["label", "true", "true_label", "gold", "y_true", "actual"])
PRED = pick(["pred", "prediction", "pred_label", "predicted", "y_pred"])
LANG = pick(["language", "lang", "source_lang", "dataset"])

if not (TEXT and TRUE and PRED):
    sys.exit(f"Could not detect columns. Edit TEXT/TRUE/PRED/LANG. Found: {list(df.columns)}")
if LANG is None:
    df["language"] = "all"
    LANG = "language"

labels = sorted(df[TRUE].unique())
print(f"\nUsing text={TEXT}, true={TRUE}, pred={PRED}, lang={LANG}")

print("\n=== Overall ===")
print(classification_report(df[TRUE], df[PRED], digits=3))

print("\n=== Val class balance per language (%) ===")
print((pd.crosstab(df[LANG], df[TRUE], normalize="index") * 100).round(1))

if train_path:
    tr = pd.read_csv(train_path)
    tl = next((c for c in ["label", "sentiment"] if c in tr.columns), None)
    tg = next((c for c in ["language", "lang", "source_lang", "dataset"] if c in tr.columns), None)
    if tl and tg:
        print("\n=== Train class balance per language (%) ===")
        print((pd.crosstab(tr[tg], tr[tl], normalize="index") * 100).round(1))

print("\n=== Per-language report + confusion matrix ===")
for lang, g in df.groupby(LANG):
    print(f"\n--- {lang} (n={len(g)}) ---")
    print(classification_report(g[TRUE], g[PRED], labels=labels, digits=3, zero_division=0))
    cm = confusion_matrix(g[TRUE], g[PRED], labels=labels)
    print(pd.DataFrame(cm, index=[f"true_{l}" for l in labels],
                       columns=[f"pred_{l}" for l in labels]))

# Misclassified Tanglish Negative rows
neg = next((l for l in labels if str(l).lower().startswith("neg")), None)
tam = df[LANG].astype(str).str.lower().str.contains("tan|tam")
if neg is not None:
    bad = df[tam & (df[TRUE] == neg) & (df[PRED] != neg)]
    print(f"\nTanglish Negative misclassified: {len(bad)}")
    print(bad[PRED].value_counts())
    bad.head(30).to_csv("data/tanglish_negative_errors.csv", index=False)
    print(bad[[TEXT, PRED]].head(30).to_string())
    print("\nSaved: data/tanglish_negative_errors.csv")

# Possible label noise: duplicate texts with conflicting labels
dup = df.groupby(TEXT)[TRUE].nunique()
print(f"\nTexts with conflicting true labels: {(dup > 1).sum()}")
print(f"Duplicate texts: {df[TEXT].duplicated().sum()}")