from datasets import load_dataset, concatenate_datasets
import pandas as pd

ds = load_dataset("community-datasets/tamilmixsentiment")
tam = concatenate_datasets([ds["train"], ds["validation"], ds["test"]]).to_pandas()
names = ds["train"].features["label"].names
tam["label"] = tam["label"].map(lambda i: names[i])

MAP = {"Positive": "Positive", "Negative": "Negative",
       "Mixed_feelings": "Neutral", "unknown_state": "Neutral"}
tam = tam[tam["label"].isin(MAP)].copy()   # drops not-Tamil
tam["label"] = tam["label"].map(MAP)
tam["language"] = "Tanglish"
print(tam["label"].value_counts())
tam[["text", "label", "language"]].to_csv("data/tamil_remapped.csv", index=False)