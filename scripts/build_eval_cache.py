"""Build evaluation cache: compute risk_scores and numpy filter probs for all images
and save them to models/eval_cache.npz for fast tuning.
"""
from __future__ import annotations

import os
import numpy as np
from pathlib import Path
import csv

from app.services.inference_service import _compute_risk_score, PRIMARY_LABEL_THRESHOLD


def load_numpy_npz(path=None):
    path = path or os.path.join(os.getcwd(), "models", "filter_numpy.npz")
    return np.load(path, allow_pickle=True)


def collect_items(dataset_root: Path):
    metadata = dataset_root / "HAM10000_metadata.csv"
    image_root = dataset_root / "imagenes"
    index = {}
    for p in image_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            index[p.stem.lower()] = p
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
    npz = load_numpy_npz()
    cols = [str(x) for x in npz["cols"].tolist()]
    mean = npz["mean"]
    std = npz["std"]
    w = npz["w"]

    items = collect_items(DATASET_ROOT)
    n = len(items)
    print("Items:", n)

    reals = []
    risk_scores = []
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
        risk_scores.append(float(risk_score))
        feat_vec = np.array([features.get(c, 0.0) for c in cols], dtype=float)
        feat_n = (feat_vec - mean) / (std + 1e-9)
        xb = np.concatenate([np.array([1.0]), feat_n])
        logit = float(xb.dot(w))
        prob = 1.0 / (1.0 + np.exp(-max(-50.0, min(50.0, logit))))
        probs.append(float(prob))

    reals = np.array(reals)
    risk_scores = np.array(risk_scores)
    probs = np.array(probs)

    out = os.path.join(os.getcwd(), "models", "eval_cache.npz")
    np.savez(out, reals=reals, risk_scores=risk_scores, probs=probs)
    print("Saved eval cache to", out)


if __name__ == "__main__":
    main()
