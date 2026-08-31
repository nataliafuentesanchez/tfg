"""Entrena un clasificador ligero (LogisticRegression) sobre features extraidas
para usar como filtro en cascada y reducir falsos positivos.
"""
from __future__ import annotations

import csv
from pathlib import Path
import cv2
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib

from app.services.inference_service import _compute_risk_score

DATASET_ROOT = Path(
    "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos"
)
METADATA_PATH = DATASET_ROOT / "HAM10000_metadata.csv"
IMAGE_ROOT = DATASET_ROOT / "imagenes"


def build_image_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for candidate in IMAGE_ROOT.rglob("*"):
        if candidate.is_file() and candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            index.setdefault(candidate.stem.lower(), candidate)
    return index


def true_label_from_dx(dx_value: str | None) -> int:
    dx = (dx_value or "").strip().lower()
    return 1 if dx not in {"nv"} else 0


def main() -> None:
    image_index = build_image_index()
    rows = list(csv.DictReader(METADATA_PATH.open("r", encoding="utf-8", newline="")))
    X = []
    y = []
    processed = 0
    for row in rows:
        image_id = (row.get("image_id") or "").strip().lower()
        file_path = image_index.get(image_id)
        if file_path is None:
            continue
        image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
        if image is None:
            continue
        processed += 1
        _, features = _compute_risk_score(image)
        feat_vec = [
            features.get("red_mean", 0.0),
            features.get("hotspot_ratio", 0.0),
            features.get("diameter_proxy", 0.0),
            features.get("asymmetry", 0.0),
            features.get("color_variance", 0.0),
            features.get("edge_density", 0.0),
            features.get("texture_variation", 0.0),
            features.get("laplacian_var", 0.0),
            features.get("hsv_mean", 0.0),
            features.get("hsv_std", 0.0),
            features.get("red_hist_0", 0.0),
            features.get("red_hist_1", 0.0),
            features.get("red_hist_2", 0.0),
            features.get("red_hist_3", 0.0),
        ]
        X.append(feat_vec)
        y.append(true_label_from_dx(row.get("dx")))

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=int)
    print("Processed", processed)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    precision = precision_score(y_test, preds)
    recall = recall_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    print(f"Filter precision={precision:.4f}, recall={recall:.4f}, f1={f1:.4f}")

    model_dir = Path.cwd() / "models"
    model_dir.mkdir(exist_ok=True)
    joblib.dump(clf, model_dir / "filter_model.joblib")
    print("Saved filter model to", model_dir / "filter_model.joblib")


if __name__ == "__main__":
    main()
