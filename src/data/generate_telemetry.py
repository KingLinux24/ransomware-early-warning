import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path("data/raw/telemetry.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

HOSTS = ["wkst-01", "wkst-02"]
USERS = ["alice", "bob"]
BENIGN_PROCS = ["chrome.exe", "onedrive.exe", "word.exe", "excel.exe"]
SUSP_PROCS = ["unknown.exe", "update_service.exe"]

DOC_EXTS = [".docx", ".xlsx", ".pptx", ".pdf", ".txt"]
RANS_EXT = ".locked"

def ts(base, seconds):
    return (base + timedelta(seconds=seconds)).isoformat() + "Z"

def random_path():
    folder = random.choice(["Documents", "Desktop", "Downloads"])
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    ext = random.choice(DOC_EXTS)
    return f"C:/Users/{random.choice(USERS)}/{folder}/{name}{ext}"

def main():
    base = datetime.utcnow() - timedelta(hours=2)
    rows = []

    # Background benign activity
    for i in range(1500):
        rows.append({
            "timestamp": ts(base, i * 2),
            "host": random.choice(HOSTS),
            "user": random.choice(USERS),
            "process_name": random.choice(BENIGN_PROCS),
            "event_type": random.choice(["file_write", "file_rename"]),
            "file_path": random_path(),
            "bytes_written": random.randint(100, 50000),
            "extension_before": None,
            "extension_after": None,
            "label": 0
        })

    # Ransomware-like burst (safe simulation)
    host = "wkst-01"
    user = "alice"
    proc = random.choice(SUSP_PROCS)

    start_attack = 4000
    for i in range(400):
        p = random_path()
        rows.append({
            "timestamp": ts(base, start_attack + i),
            "host": host,
            "user": user,
            "process_name": proc,
            "event_type": "file_write",
            "file_path": p,
            "bytes_written": random.randint(20000, 200000),
            "extension_before": None,
            "extension_after": None,
            "label": 1
        })
        rows.append({
            "timestamp": ts(base, start_attack + i + 0.2),
            "host": host,
            "user": user,
            "process_name": proc,
            "event_type": "file_rename",
            "file_path": p + RANS_EXT,
            "bytes_written": 0,
            "extension_before": p.split(".")[-1],
            "extension_after": RANS_EXT.replace(".", ""),
            "label": 1
        })

    random.shuffle(rows)

    with OUT.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    main()
