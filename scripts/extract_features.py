"""Extrae features para cada imagen del dataset y guarda un CSV con las
características usadas para el ajuste de reglas.
"""
from __future__ import annotations

import csv
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

    out_path = Path.cwd() / "models" / "features.csv"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = None
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
            record = {
                "image_id": image_id,
                "filename": file_path.name,
                "actual": true_label_from_dx(row.get("dx")),
                "risk_score": float(risk_score),
            }
            record.update(features)
            if writer is None:
                writer = csv.DictWriter(fh, fieldnames=list(record.keys()))
                writer.writeheader()
            writer.writerow(record)

    print("Wrote features for", processed, "images to", out_path)


if __name__ == "__main__":
    main()
