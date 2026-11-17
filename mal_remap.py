import re
import pandas as pd

D = "data/dravidiancodemix/DravidianCodeMix/"
FILES = ["mal_full_sentiment_train.csv", "mal_full_sentiment_dev.csv",
         "mal_full_sentiment_test.csv"]
PAT = re.compile(
    r"(.*?);(Positive|Negative|Mixed_feelings|unknown_state|not-malayalam);[ \t]*(?:\r?\n|$)",
    re.S)
MAP = {"Positive": "Positive", "Negative": "Negative",
       "Mixed_feelings": "Neutral", "unknown_state": "Neutral"}

rows = []
for f in FILES:
    raw = open(D + f, encoding="utf-8", errors="replace").read()
    found = [(re.sub(r"\s+", " ", t).strip(), l) for t, l in PAT.findall(raw)]
    print(f, "rows parsed:", len(found))
    rows += found

df = pd.DataFrame(rows, columns=["text", "raw_label"])
print("\nRaw label counts:\n", df["raw_label"].value_counts())

df = df[df["raw_label"].isin(MAP)].copy()
df["label"] = df["raw_label"].map(MAP)
df = df[df["text"].str.len() > 0].drop_duplicates("text")
df["language"] = "Manglish"
print("\nFinal label counts:\n", df["label"].value_counts())
df[["text", "label", "language"]].to_csv("data/mal_remapped.csv", index=False)
print("\nSaved data/mal_remapped.csv", df.shape)