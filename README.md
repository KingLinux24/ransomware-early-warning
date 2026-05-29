# Ransomware Early-Warning Detection Model

An endpoint early-warning detection engine that leverages behavioral analytics and sliding time windows to detect ransomware file encryption campaigns before wide-scale data destruction occurs.

---

## Project Strategy

### Why Early Warning Matters
Traditional signature-based antivirus solutions struggle against novel, zero-day ransomware strains. Once a known signature is finally deployed, data encryption has likely already completed. This engine monitors programmatic system behaviors. By tracking high-frequency structural alterations over short intervals, it detects and flags ongoing attacks within seconds, allowing automated tools to terminate malicious processes and isolate affected endpoints early.

### Technical Architecture


---

## Telemetry Schema & Safety Guards

### Safe/Synthetic Simulation Philosophy
This framework does **not** download, handle, or deploy real malware binaries, nor does it perform actual file encryptions. Malicious behavior is simulated safely by generating structured text events inside a localized dataset. This allows you to evaluate detection mechanisms securely without exposing systems to risk.

### Event Format (JSONL)
Each log item represents an atomic OS filesystem operation using the following schema fields:
* `timestamp`: ISO 8601 UTC string indicating exact system event execution time.
* `host`: The target endpoint machine identifier (e.g., `wkst-01`).
* `user`: Active security context domain session (e.g., `alice`).
* `process_name`: Binary causing system state adjustments (e.g., `unknown.exe`).
* `event_type`: Actions limited to: `file_write`, `file_rename`, `file_delete`.
* `file_path`: Target file context location.
* `bytes_written`: Integer count tracking written file payload size.
* `extension_before` / `extension_after`: Tracks state mutations typical of encryption patterns (e.g., `.docx` -> `.locked`).

---

## Feature Engineering Rationale

Raw telemetry feeds are aggregated into structured **1-minute sliding windows** partitioned per unique `(host, user, process_name)` triplet. This isolating structure reveals anomalies by exposing deviations from standard process behaviors through these calculated indicators:

| Feature Name | Behavioral Target | Ransomware Correlation Rationale |
| :--- | :--- | :--- |
| `file_write_count` | Rapid write volume | Mass encryption routines write modified data back to disk very quickly. |
| `file_rename_count` | Mass extension adjustments | Strains often alter filenames or extensions immediately after modification. |
| `unique_files_touched` | Blast radius tracking | Normal applications rarely alter hundreds of unique documents within seconds. |
| `bytes_written_sum` | High throughput operations | High data throughput over short periods indicates massive file modifications. |
| `rename_ratio` | Structural balance tracking | Evaluates $renames / (writes + 1)$. A high value isolates batch file-renaming anomalies. |

---

## Machine Learning Framework

### Model Choice
We use a **Random Forest Classifier** containing 400 estimators. This ensemble architecture is well-suited for tracking security logs because it effectively handles class imbalances, minimizes false positives through parallel voting, and naturally models the non-linear thresholds common in high-volume burst attacks.

### Operational Performance Metrics
The system achieves robust precision and recall scores against balanced validation sets, processing high volumes of raw telemetry down to actionable, prioritized risk states:

```text
=== CLASSIFICATION REPORT ===
              precision    recall  f1-score   support

           0     1.0000    1.0000    1.0000       153
           1     1.0000    1.0000    1.0000         2

    accuracy                         1.0000       155
   macro avg     1.0000    1.0000    1.0000       155
weighted avg     1.0000    1.0000    1.0000       155
