"""Fast vectorized sweep for NumPy filter cutoff.

Computes risk_score and numpy-filter probability for every image once,
then evaluates thresholds quickly to pick the best cutoff. Saves cutoff
into models/filter_numpy.npz.
"""
from __future__ import annotations

import os
import numpy as np
from pathlib import Path
import csv

from app.services.inference_service import _compute_risk_score, PRIMARY_LABEL_THRESHOLD


def load_numpy_filter_npz(path: str = None):
    path = path or os.path.join(os.getcwd(), "models", "filter_numpy.npz")
    if not os.path.exists(path):
        return None
    data = np.load(path, allow_pickle=True)
    return data


def build_index(dataset_root: Path):
    image_root = dataset_root / "imagenes"
    index = {}
    for p in image_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            index[p.stem.lower()] = p
    return index


def collect_pairs(dataset_root: Path):
    metadata = dataset_root / "HAM10000_metadata.csv"
    index = build_index(dataset_root)
    rows = list(csv.DictReader(metadata.open("r", encoding="utf-8", newline="")))
    items = []
    for row in rows:
        image_id = (row.get("image_id") or "").strip().lower()
        p = index.get(image_id)
        if not p:
            continue
        label = "ENFERMO" if (row.get("dx") or "").strip().lower() not in {"nv"} else "SANO"
        items.append((p, label))
    return items


def main():
    DATASET_ROOT = Path(
        "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos"
    )
    numpy_npz = load_numpy_filter_npz()
    if numpy_npz is None:
        print("No numpy model found")
        return

    cols = [str(x) for x in numpy_npz["cols"].tolist()]
    mean = numpy_npz["mean"]
    std = numpy_npz["std"]
    w = numpy_npz["w"]

    items = collect_pairs(DATASET_ROOT)
    n = len(items)
    print("Collected", n, "items")

    reals = []
    primary_labels = []
    probs = []

    import cv2

    for p, label in items:
        try:
            content = p.read_bytes()
            img = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
            risk_score, features = _compute_risk_score(img)
        except Exception:
            continue
        reals.append(label)
        primary_labels.append("ENFERMO" if risk_score >= PRIMARY_LABEL_THRESHOLD else "SANO")
        feat_vec = np.array([features.get(c, 0.0) for c in cols], dtype=float)
        feat_n = (feat_vec - mean) / (std + 1e-9)
        xb = np.concatenate([np.array([1.0]), feat_n])
        logit = float(xb.dot(w))
        prob = 1.0 / (1.0 + np.exp(-max(-50.0, min(50.0, logit))))
        probs.append(prob)

    reals = np.array(reals)
    primary_labels = np.array(primary_labels)
    probs = np.array(probs)

    thresholds = np.linspace(0.0, 0.99, 100)
    best = None
    best_stats = None

    def metrics_for_preds(real_arr, pred_arr):
        tp = np.sum((real_arr == "ENFERMO") & (pred_arr == "ENFERMO"))
        tn = np.sum((real_arr == "SANO") & (pred_arr == "SANO"))
        fp = np.sum((real_arr == "SANO") & (pred_arr == "ENFERMO"))
        fn = np.sum((real_arr == "ENFERMO") & (pred_arr == "SANO"))
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
        return {"tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn), "precision": precision, "recall": recall, "f1": f1, "acc": acc}

    for cutoff in thresholds:
        preds = np.where(probs >= cutoff, "SANO", primary_labels)
        stats = metrics_for_preds(reals, preds)
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
        # save cutoff
        path = os.path.join(os.getcwd(), "models", "filter_numpy.npz")
        data = dict(np.load(path, allow_pickle=True))
        data["cutoff"] = np.array(cutoff)
        np.savez(path, **data)
        print("Saved cutoff into", path)


if __name__ == "__main__":
    main()
