import pandas as pd
import joblib
from pathlib import Path

DATA = Path("data/processed/window_features.csv")
MODEL = Path("src/models/ransomware_rf.joblib")

def main():
    df = pd.read_csv(DATA)
    df["window"] = pd.to_datetime(df["window"])

    model = joblib.load(MODEL)

    feature_cols = [
        "file_write_count",
        "file_rename_count",
        "unique_files_touched",
        "bytes_written_sum",
        "rename_ratio",
    ]

    df["prob"] = model.predict_proba(df[feature_cols])[:, 1]
    threshold = 0.8
    df["alert"] = df["prob"] >= threshold

    # Find first ransomware window per (host,user,proc)
    attack_groups = df[df["ransomware_label"] == 1].groupby(["host", "user", "process_name"])
    for key, g in attack_groups:
        start = g["window"].min()
        g_all = df[(df["host"] == key[0]) & (df["user"] == key[1]) & (df["process_name"] == key[2])].copy()

        first_alert = g_all[g_all["alert"] == True]["window"].min()
        if pd.isna(first_alert):
            print(f"{key}: no alert triggered")
        else:
            delta = (first_alert - start).total_seconds()
            print(f"{key}: time-to-detect = {delta:.0f} seconds (threshold={threshold})")

if __name__ == "__main__":
    main()
