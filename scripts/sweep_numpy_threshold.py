"""Barrido de umbrales para el filtro NumPy.

Carga el modelo `models/filter_numpy.npz`, recorre el dataset HAM10000 (misma
lógica que `scripts/evaluate_baseline_ham10000.py`) y evalúa métricas para
varios umbrales. Selecciona el umbral que maximiza precisión sujeta a recall
>= 0.65; si ninguno lo cumple, selecciona el umbral con mayor F1.

Guarda el umbral elegido dentro del archivo NPZ (clave 'cutoff').
"""
from __future__ import annotations

import os
import numpy as np
from collections import Counter

from app.services.inference_service import _compute_risk_score, PRIMARY_LABEL_THRESHOLD


def load_numpy_filter():
    path = os.path.join(os.getcwd(), "models", "filter_numpy.npz")
    if not os.path.exists(path):
        return None
    data = np.load(path, allow_pickle=True)
    return {
        "w": data["w"],
        "mean": data["mean"],
        "std": data["std"],
        "cols": [str(x) for x in data["cols"].tolist()],
    }


def iterate_images():
    # Use same dataset layout as evaluate_baseline_ham10000.py
    from pathlib import Path
    import csv

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

    if not METADATA_PATH.exists() or not IMAGE_ROOT.exists():
        return

    image_index = build_image_index()
    rows = list(csv.DictReader(METADATA_PATH.open("r", encoding="utf-8", newline="")))
    for row in rows:
        image_id = (row.get("image_id") or "").strip().lower()
        file_path = image_index.get(image_id)
        if file_path is None:
            continue
        try:
            content = file_path.read_bytes()
        except Exception:
            continue
        yield content, ("ENFERMO" if (row.get("dx") or "").strip().lower() not in {"nv"} else "SANO")


def compute_metrics(results):
    tp = tn = fp = fn = 0
    for real, pred in results:
        if real == "ENFERMO":
            if pred == "ENFERMO":
                tp += 1
            else:
                fn += 1
        else:
            if pred == "SANO":
                tn += 1
            else:
                fp += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    acc = (tp + tn) / (tp + tn + fp + fn)
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1, "acc": acc}


def main():
    numpy_filter = load_numpy_filter()
    if numpy_filter is None:
        print("No numpy filter found at models/filter_numpy.npz")
        return

    cols = numpy_filter["cols"]
    mean = numpy_filter["mean"]
    std = numpy_filter["std"]
    w = numpy_filter["w"]

    thresholds = np.linspace(0.0, 0.99, 100)
    best = None
    best_stats = None

    all_items = list(iterate_images())
    total = len(all_items)
    print("Found", total, "images to evaluate")

    for cutoff in thresholds:
        results = []
        for content, real_label in all_items:
            try:
                risk_score, features = _compute_risk_score(__import__('cv2').imdecode(np.frombuffer(content, np.uint8), __import__('cv2').IMREAD_COLOR))
            except Exception:
                # fallback using analyze_image would decode already; skip
                continue
            primary_label = "ENFERMO" if risk_score >= PRIMARY_LABEL_THRESHOLD else "SANO"

            # compute numpy filter prob
            feat_vec = np.array([features.get(c, 0.0) for c in cols], dtype=float)
            feat_n = (feat_vec - mean) / (std + 1e-9)
            xb = np.concatenate([np.array([1.0]), feat_n])
            logit = float(xb.dot(w))
            prob = 1.0 / (1.0 + np.exp(-max(-50.0, min(50.0, logit))))
            # apply suppression: if prob >= cutoff -> predict SANO
            if prob >= cutoff:
                pred = "SANO"
            else:
                pred = primary_label

            results.append((real_label, pred))

        stats = compute_metrics(results)
        # choose best: prefer precision with recall >=0.65
        if stats["recall"] >= 0.65:
            score = stats["precision"]
        else:
            score = stats["f1"]

        if best is None or score > best:
            best = score
            best_stats = (cutoff, stats)

    if best_stats:
        cutoff, stats = best_stats
        print("Selected cutoff:", cutoff)
        print(stats)
        # Save cutoff into npz
        path = os.path.join(os.getcwd(), "models", "filter_numpy.npz")
        data = np.load(path, allow_pickle=True)
        save_dict = {k: data[k] for k in data.files}
        save_dict["cutoff"] = np.array(cutoff)
        np.savez(path, **save_dict)
        print("Saved cutoff into", path)


if __name__ == "__main__":
    main()
