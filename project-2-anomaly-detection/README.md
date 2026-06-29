# Project 2: Network Anomaly Detection 📊

> **The "Data Science Flex"** — proving I can look at millions of log entries and use statistics to find a needle in a haystack.

## What This Does

Builds a machine learning pipeline to classify network traffic as **normal**, **DoS/DDoS**, **probe**, **R2L**, or **U2R** using the NSL-KDD benchmark dataset.

Two complementary approaches:
- **Supervised** — Random Forest classifier trained on labelled attack data
- **Unsupervised** — Isolation Forest to flag anomalies without needing labels (closer to real-world SIEM behaviour)

---

## Dataset

**NSL-KDD** — the standard benchmark for network intrusion detection research.

Download: https://www.unb.ca/cic/datasets/nsl.html  
File needed: `KDDTrain+.txt`

> Don't have the dataset yet? Run the script with no arguments — it generates synthetic data to demonstrate the pipeline.

---

## How to Run

```bash
pip install -r requirements.txt

# With NSL-KDD dataset
python anomaly_detector.py --data KDDTrain+.txt

# Demo mode (synthetic data)
python anomaly_detector.py
```

---

## Key Features

### Feature Engineering
The model uses traffic features most predictive of attack behaviour:

| Feature | Why it matters |
|---------|---------------|
| `serror_rate` | High SYN error rate → SYN flood (DDoS) |
| `count` | Connections to same host in 2s window → brute force / flood |
| `src_bytes` | Near-zero bytes → probe scanning |
| `same_srv_rate` | High rate to single service → targeted attack |
| `dst_host_count` | Wide spread → port scan |

### Why Two Models?
Real Security Operations Centers face two problems:

1. **Known attack patterns** → Random Forest (supervised) catches these reliably
2. **Zero-day / novel attacks** → Isolation Forest (unsupervised) flags statistical outliers, even without training labels

Combining both mirrors how enterprise SIEM platforms like Splunk and Microsoft Sentinel work.

### Reducing False Positives
A naive model triggers thousands of false alerts per day — "alert fatigue" causes analysts to start ignoring them. This pipeline is tuned using precision/recall tradeoffs so human analysts see fewer but higher-confidence alerts.

---

## Results (on NSL-KDD)
Expected approximate performance with full dataset:

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| normal | ~0.98 | ~0.97 | ~0.97 |
| dos | ~0.99 | ~0.99 | ~0.99 |
| probe | ~0.93 | ~0.90 | ~0.91 |
| r2l | ~0.85 | ~0.80 | ~0.82 |
| u2r | ~0.70 | ~0.65 | ~0.67 |

U2R attacks are hardest — very few training examples (class imbalance). A real system would use SMOTE or cost-sensitive learning to address this.
