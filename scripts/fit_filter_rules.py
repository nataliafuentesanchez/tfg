"""Genera reglas heurísticas para filtrar falsos positivos basadas en
percentiles de features calculadas sobre HAM10000.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import cv2
import numpy as np

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


def true_label_from_dx(dx_value: str | None) -> str:
    dx = (dx_value or "").strip().lower()
    return "ENFERMO" if dx not in {"nv"} else "SANO"


def main() -> None:
    image_index = build_image_index()
    rows = list(csv.DictReader(METADATA_PATH.open("r", encoding="utf-8", newline="")))

    tp_feats = {k: [] for k in ["diameter_proxy", "hotspot_ratio", "color_variance", "laplacian_var"]}
    fp_feats = {k: [] for k in ["diameter_proxy", "hotspot_ratio", "color_variance", "laplacian_var"]}

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
        risk_score, features = _compute_risk_score(image)
        predicted = "ENFERMO" if risk_score >= 0.50 else "SANO"
        actual = true_label_from_dx(row.get("dx"))
        if predicted == "ENFERMO" and actual == "ENFERMO":
            for k in tp_feats:
                tp_feats[k].append(features.get(k, 0.0))
        if predicted == "ENFERMO" and actual == "SANO":
            for k in fp_feats:
                fp_feats[k].append(features.get(k, 0.0))

    print("Processed", processed)
    rules = {}
    # Choose conservative thresholds: 10th percentile of TP features
    for k in tp_feats:
        if len(tp_feats[k]) > 0:
            th = float(np.percentile(tp_feats[k], 10))
        else:
            th = 0.0
        rules[k + "_min"] = th

    model_dir = Path.cwd() / "models"
    model_dir.mkdir(exist_ok=True)
    with open(model_dir / "filter_rules.json", "w", encoding="utf-8") as fh:
        json.dump(rules, fh, indent=2)
    print("Saved rules to", model_dir / "filter_rules.json")


if __name__ == "__main__":
    main()
