"""Grid search over primary_threshold and numpy cutoff to maximize precision
subject to recall >= 0.65 (fallback: maximize F1). Saves best params to
models/filter_params.json and updates models/filter_numpy.npz with cutoff.
"""
from __future__ import annotations

import json
import os
import numpy as np


def load_cache(path=None):
    path = path or os.path.join(os.getcwd(), "models", "eval_cache.npz")
    return np.load(path, allow_pickle=True)


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


def main():
    data = load_cache()
    reals = data["reals"]
    risk_scores = data["risk_scores"]
    probs = data["probs"]

    primary_grid = np.linspace(0.45, 0.75, 16)
    cutoff_grid = np.linspace(0.0, 0.99, 100)

    best = None
    best_meta = None

    for pt in primary_grid:
        for cutoff in cutoff_grid:
            preds = np.where(probs >= cutoff, "SANO", np.where(risk_scores >= pt, "ENFERMO", "SANO"))
            stats = metrics_for_preds(reals, preds)
            if stats["recall"] >= 0.65:
                score = stats["precision"]
            else:
                score = stats["f1"]
            if best is None or score > best:
                best = score
                best_meta = {"primary_threshold": float(pt), "cutoff": float(cutoff), "stats": stats}

    if best_meta:
        print("Best:", best_meta)
        out = os.path.join(os.getcwd(), "models", "filter_params.json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(best_meta, fh, indent=2)
        # update npz cutoff
        npz_path = os.path.join(os.getcwd(), "models", "filter_numpy.npz")
        d = dict(np.load(npz_path, allow_pickle=True))
        d["cutoff"] = np.array(best_meta["cutoff"])
        np.savez(npz_path, **d)
        print("Saved params and updated npz cutoff")


if __name__ == "__main__":
    main()
