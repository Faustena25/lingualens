from datasets import load_dataset, get_dataset_config_names
from collections import Counter

for name in ["community-datasets/tamilmixsentiment",
             "bharathichezhiyan/DravidianCodeMix-Dataset"]:
    print("\n=====", name, "=====")
    try:
        configs = get_dataset_config_names(name)
    except Exception as e:
        configs = [None]
        print("configs lookup failed:", e)
    print("configs:", configs)
    for cfg in configs:
        try:
            ds = load_dataset(name, cfg) if cfg else load_dataset(name)
        except Exception as e:
            print(f"[{cfg}] load failed: {e}")
            continue
        for split, d in ds.items():
            col = next((c for c in d.column_names
                        if c in ("label", "sentiment", "Label")), None)
            if col is None:
                print(f"[{cfg}/{split}] columns: {d.column_names}")
                continue
            feat = d.features[col]
            names = getattr(feat, "names", None)
            vals = d[col]
            if names:
                vals = [names[v] for v in vals]
            print(f"[{cfg}/{split}] {dict(Counter(vals))}")