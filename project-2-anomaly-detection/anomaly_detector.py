"""
Network Anomaly Detection — DDoS vs Normal Traffic Classifier

Dataset: NSL-KDD (improved version of KDD Cup 1999)
Download: https://www.unb.ca/cic/datasets/nsl.html

This script:
1. Loads and preprocesses the NSL-KDD dataset
2. Engineers features for ML
3. Trains a Random Forest classifier
4. Evaluates performance with precision/recall/F1
5. Highlights statistical anomalies using Isolation Forest (unsupervised)

Usage:
    python anomaly_detector.py --data KDDTrain+.txt

If no data file is provided, a synthetic dataset is generated for demo.
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings("ignore")


# ── NSL-KDD Column Names ──────────────────────────────────────────────────────

NSL_KDD_COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins",
    "logged_in", "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty"
]

ATTACK_CATEGORIES = {
    "normal": "normal",
    # DoS / DDoS
    "neptune": "dos", "back": "dos", "land": "dos", "pod": "dos",
    "smurf": "dos", "teardrop": "dos", "apache2": "dos", "udpstorm": "dos",
    "processtable": "dos", "mailbomb": "dos",
    # Probe
    "satan": "probe", "ipsweep": "probe", "nmap": "probe", "portsweep": "probe",
    "mscan": "probe", "saint": "probe",
    # R2L
    "guess_passwd": "r2l", "ftp_write": "r2l", "imap": "r2l", "phf": "r2l",
    "multihop": "r2l", "warezmaster": "r2l", "warezclient": "r2l", "spy": "r2l",
    # U2R
    "buffer_overflow": "u2r", "loadmodule": "u2r", "rootkit": "u2r", "perl": "u2r",
}


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_nsl_kdd(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, names=NSL_KDD_COLUMNS)
    df["attack_category"] = df["label"].str.lower().map(
        lambda x: ATTACK_CATEGORIES.get(x, "unknown")
    )
    return df


def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic network traffic for demo when no dataset is available."""
    print("[!] No dataset provided — generating synthetic data for demonstration.\n")
    rng = np.random.default_rng(42)

    n_normal = int(n_samples * 0.6)
    n_dos    = int(n_samples * 0.25)
    n_probe  = n_samples - n_normal - n_dos

    normal = pd.DataFrame({
        "duration":        rng.exponential(5,   n_normal),
        "src_bytes":       rng.normal(5000, 1000, n_normal).clip(0),
        "dst_bytes":       rng.normal(8000, 2000, n_normal).clip(0),
        "count":           rng.integers(1, 50,   n_normal),
        "serror_rate":     rng.beta(1, 20,        n_normal),
        "rerror_rate":     rng.beta(1, 20,        n_normal),
        "same_srv_rate":   rng.beta(8, 2,         n_normal),
        "dst_host_count":  rng.integers(1, 255,  n_normal),
        "attack_category": "normal",
    })

    dos = pd.DataFrame({
        "duration":        rng.exponential(0.1, n_dos),
        "src_bytes":       rng.normal(0, 10,     n_dos).clip(0),
        "dst_bytes":       rng.normal(0, 5,      n_dos).clip(0),
        "count":           rng.integers(400, 512, n_dos),
        "serror_rate":     rng.beta(8, 2,         n_dos),
        "rerror_rate":     rng.beta(1, 5,         n_dos),
        "same_srv_rate":   rng.beta(9, 1,         n_dos),
        "dst_host_count":  rng.integers(200, 255, n_dos),
        "attack_category": "dos",
    })

    probe = pd.DataFrame({
        "duration":        rng.exponential(2,    n_probe),
        "src_bytes":       rng.normal(300, 100,  n_probe).clip(0),
        "dst_bytes":       rng.normal(0, 50,     n_probe).clip(0),
        "count":           rng.integers(1, 20,   n_probe),
        "serror_rate":     rng.beta(2, 5,         n_probe),
        "rerror_rate":     rng.beta(4, 3,         n_probe),
        "same_srv_rate":   rng.beta(2, 5,         n_probe),
        "dst_host_count":  rng.integers(100, 255, n_probe),
        "attack_category": "probe",
    })

    df = pd.concat([normal, dos, probe], ignore_index=True).sample(frac=1, random_state=42)
    return df


# ── Preprocessing ─────────────────────────────────────────────────────────────

FEATURES = [
    "duration", "src_bytes", "dst_bytes", "count",
    "serror_rate", "rerror_rate", "same_srv_rate", "dst_host_count"
]


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, LabelEncoder]:
    # Encode categorical columns if present (NSL-KDD)
    for col in ["protocol_type", "service", "flag"]:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))

    available = [f for f in FEATURES if f in df.columns]
    X = df[available].fillna(0).values

    le = LabelEncoder()
    y = le.fit_transform(df["attack_category"])

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    return X, y, le


# ── Model Training & Evaluation ───────────────────────────────────────────────

def train_and_evaluate(X, y, le):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("── Supervised: Random Forest Classifier ────────────────────────")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(classification_report(y_test, y_pred, target_names=le.classes_))

    print("\n── Unsupervised: Isolation Forest (Anomaly Score) ──────────────")
    iso = IsolationForest(contamination=0.3, random_state=42)
    anomaly_labels = iso.fit_predict(X)
    n_anomalies = (anomaly_labels == -1).sum()
    print(f"Isolation Forest flagged {n_anomalies} / {len(X)} samples as anomalous")
    print(f"({100 * n_anomalies / len(X):.1f}% of traffic)\n")

    print("── Feature Importances (Random Forest) ─────────────────────────")
    available = [f for f in FEATURES if f in [
        "duration", "src_bytes", "dst_bytes", "count",
        "serror_rate", "rerror_rate", "same_srv_rate", "dst_host_count"
    ]]
    importances = sorted(
        zip(available, clf.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    for feat, imp in importances:
        bar = "█" * int(imp * 50)
        print(f"  {feat:<30} {bar} {imp:.4f}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Anomaly Detector")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to NSL-KDD dataset (KDDTrain+.txt)")
    args = parser.parse_args()

    if args.data:
        print(f"[*] Loading NSL-KDD dataset from {args.data}...")
        df = load_nsl_kdd(args.data)
    else:
        df = generate_synthetic_data()

    print(f"[*] Dataset shape: {df.shape}")
    print(f"[*] Class distribution:\n{df['attack_category'].value_counts()}\n")

    X, y, le = preprocess(df)
    train_and_evaluate(X, y, le)
