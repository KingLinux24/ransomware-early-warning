import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

DATA = Path("data/processed/window_features.csv")
MODEL_OUT = Path("src/models/ransomware_rf.joblib")

def main():
    df = pd.read_csv(DATA)

    feature_cols = [
        "file_write_count",
        "file_rename_count",
        "unique_files_touched",
        "bytes_written_sum",
        "rename_ratio",
    ]

    X = df[feature_cols]
    y = df["ransomware_label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print(classification_report(y_test, preds, digits=4))

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT)

if __name__ == "__main__":
    main()
