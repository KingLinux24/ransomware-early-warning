import pandas as pd
import joblib
from pathlib import Path

DATA = Path("data/processed/window_features.csv")
MODEL = Path("src/models/ransomware_rf.joblib")
OUT = Path("data/processed/alerts.csv")

def main():
    df = pd.read_csv(DATA)
    model = joblib.load(MODEL)

    feature_cols = [
        "file_write_count",
        "file_rename_count",
        "unique_files_touched",
        "bytes_written_sum",
        "rename_ratio",
    ]

    df["malicious_prob"] = model.predict_proba(df[feature_cols])[:, 1]
    threshold = 0.8
    alerts = df[df["malicious_prob"] >= threshold].copy()
    alerts = alerts.sort_values("malicious_prob", ascending=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    alerts.to_csv(OUT, index=False)

if __name__ == "__main__":
    main()
