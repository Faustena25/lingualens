import pandas as pd
from sklearn.model_selection import train_test_split

old = pd.read_csv("data/unified.csv")
print("old columns:", list(old.columns))
print(old["split"].value_counts())

names = {k: next((s for s in old["split"].unique() if k in str(s).lower()), None)
         for k in ["train", "val", "test"]}
names["val"] = names["val"] or next(
    (s for s in old["split"].unique() if "dev" in str(s).lower()), None)
print("split names:", names)

hin = old[old["language"] == "Hinglish"].copy()
idx = hin[hin["split"] == "validation"].sample(frac=0.5, random_state=42).index
hin.loc[idx, "split"] = "test"

new = pd.concat([pd.read_csv("data/tamil_remapped.csv"),
                 pd.read_csv("data/mal_remapped.csv")], ignore_index=True)
new["strat"] = new["language"] + "_" + new["label"]
tr, rest = train_test_split(new, test_size=0.2, stratify=new["strat"], random_state=42)
va, te = train_test_split(rest, test_size=0.5, stratify=rest["strat"], random_state=42)
tr = tr.assign(split=names["train"])
va = va.assign(split=names["val"])
te = te.assign(split=names["test"] or names["val"])

cols = ["text", "label", "language", "split"]
out = pd.concat([hin[cols], tr[cols], va[cols], te[cols]], ignore_index=True)
out = out.sample(frac=1, random_state=42).reset_index(drop=True)
out.to_csv("data/unified_v2.csv", index=False)
print(out.shape)
print(pd.crosstab(out["language"], out["label"]))
print(pd.crosstab(out["language"], out["split"]))