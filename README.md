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

```

Getting Started & Execution Guide
Follow these steps to clone, configure, and execute the ransomware early-warning detection pipeline on your local machine.

1. Prerequisites & Cloning
Ensure you have Python 3.8+ installed on your host system. Clone the repository and navigate to the project root directory:

```Bash
git clone https://github.com/<your-username>/ransomware-early-warning.git
cd ransomware-early-warning
```
2. Environment Setup
Initialize a localized virtual environment to isolate the project dependency packages, then upgrade package management utilities:

```Bash
# Create the virtual environment
python -m venv .venv
```
# Activate the environment
# On Linux/macOS:
```
source .venv/bin/activate
```
# On Windows (Command Prompt):
```
.venv\Scripts\activate.bat
```
# On Windows (PowerShell):
```
.venv\Scripts\Activate.ps1
```
# Upgrade pip and install the required modules
```
pip install -U pip
pip install -r requirements.txt
```
3. Executing the Data Pipeline
The detection engine relies on data flows moving from raw telemetry ingestion to live validation. Run each component sequentially, or execute the master compound script statement below:

Step-by-Step Commands:
```Bash
# Step A: Generate safe, synthetic background and attack telemetry logs
python src/data/generate_telemetry.py

# Step B: Process raw JSONL logs into 1-minute behavioral window metrics
python src/features/build_features.py

# Step C: Train the Random Forest Classifier and export the model state
python src/models/train.py

# Step D: Process telemetry through the model to identify malicious anomalies
python src/detection/detect.py

# Step E: Calculate the operational Time-to-Detect response delta
python src/models/time_to_detect.py
Monolithic One-Shot Execution:

python src/data/generate_telemetry.py && python src/features/build_features.py && python src/models/train.py && python src/detection/detect.py && python src/models/time_to_detect.py
```
4. Running the Threat Alert API
Once the pipeline has processed the features and flags, you can serve the active alerts over a local web service network:

```Bash
uvicorn src.api.app:app --reload --port 8000
```
Interactive API Playground Docs: Open your browser and navigate to http://127.0.0.1:8000/docs to review and execute real-time payload queries.

Retrieve Detection List: Send an HTTP GET request to http://127.0.0.1:8000/alerts to access your prioritized threat arrays in JSON format.
