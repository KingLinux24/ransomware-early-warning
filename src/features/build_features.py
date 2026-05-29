import json
import pandas as pd
from pathlib import Path

IN_PATH = Path("data/raw/telemetry.jsonl")
OUT_PATH = Path("data/processed/window_features.csv")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def main():
    rows = []
    with IN_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["window"] = df["timestamp"].dt.floor("1min")

    df["is_write"] = (df["event_type"] == "file_write").astype(int)
    df["is_rename"] = (df["event_type"] == "file_rename").astype(int)

    grouped = df.groupby(["host", "user", "process_name", "window"]).agg(
        file_write_count=("is_write", "sum"),
        file_rename_count=("is_rename", "sum"),
        unique_files_touched=("file_path", "nunique"),
        bytes_written_sum=("bytes_written", "sum"),
        ransomware_label=("label", "max")
    ).reset_index()

    grouped["rename_ratio"] = grouped["file_rename_count"] / (grouped["file_write_count"] + 1)

    grouped.to_csv(OUT_PATH, index=False)

if __name__ == "__main__":
    main()
