# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import cv2

from app.services.inference_service import _compute_risk_score, analyze_image

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


def classify_by_risk(risk_score: float) -> str:
    return "ENFERMO" if risk_score >= 0.50 else "SANO"


def true_label_from_dx(dx_value: str | None) -> str:
    dx = (dx_value or "").strip().lower()
    return "ENFERMO" if dx not in {"nv"} else "SANO"


def main() -> None:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV de metadatos: {METADATA_PATH}")
    if not IMAGE_ROOT.exists():
        raise FileNotFoundError(f"No existe la carpeta de imagenes: {IMAGE_ROOT}")

    image_index = build_image_index()
    rows = list(csv.DictReader(METADATA_PATH.open("r", encoding="utf-8", newline="")))

    real_counts: Counter[str] = Counter()
    pred_counts: Counter[str] = Counter()
    confusion = {"SANO": {"SANO": 0, "ENFERMO": 0}, "ENFERMO": {"SANO": 0, "ENFERMO": 0}}
    tp = fp = fn = tn = 0
    processed = 0

    for row in rows:
        image_id = (row.get("image_id") or "").strip().lower()
        file_path = image_index.get(image_id)
        if file_path is None:
            continue

        # Use analyze_image (bytes) so any cascaded filters or rules are applied
        try:
            content = file_path.read_bytes()
            resp = analyze_image(content, filename=file_path.name)
            risk_score = float(resp.risk_score)
        except Exception:
            # Fallback to direct feature scoring
            image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
            if image is None:
                continue
            risk_score, _ = _compute_risk_score(image)

        processed += 1
        predicted = classify_by_risk(risk_score)
        actual = true_label_from_dx(row.get("dx"))

        real_counts[actual] += 1
        pred_counts[predicted] += 1
        confusion[actual][predicted] += 1

        if actual == "ENFERMO" and predicted == "ENFERMO":
            tp += 1
        elif actual == "SANO" and predicted == "SANO":
            tn += 1
        elif actual == "SANO" and predicted == "ENFERMO":
            fp += 1
        elif actual == "ENFERMO" and predicted == "SANO":
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0

    print("PROCESSED_IMAGES", processed)
    print("REAL_COUNTS", dict(real_counts))
    print("PRED_COUNTS", dict(pred_counts))
    print("CONFUSION_MATRIX", confusion)
    print("COUNTS", {"TP": tp, "TN": tn, "FP": fp, "FN": fn})
    print(f"PRECISION={precision:.4f}")
    print(f"RECALL={recall:.4f}")
    print(f"F1={f1:.4f}")
    print(f"ACCURACY={accuracy:.4f}")


if __name__ == "__main__":
    main()
