"""Grid search simple sobre thresholds heurísticos para maximizar F1 con
restricción de recall mínimo.
"""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import numpy as np

FEATURES_PATH = Path.cwd() / "models" / "features.csv"
OUT_PATH = Path.cwd() / "models" / "filter_rules_tuned.json"


def evaluate_thresholds(df: pd.DataFrame, rules: dict) -> dict:
    tp = fp = tn = fn = 0
    for _, row in df.iterrows():
        predicted = "ENFERMO" if row["risk_score"] >= 0.50 else "SANO"
        if predicted == "ENFERMO":
            suppress = False
            if row.get("diameter_proxy", 0.0) < rules.get("diameter_proxy_min", 0.0):
                suppress = True
            if row.get("hotspot_ratio", 0.0) < rules.get("hotspot_ratio_min", 0.0):
                suppress = True
            if row.get("color_variance", 0.0) < rules.get("color_variance_min", 0.0):
                suppress = True
            if row.get("laplacian_var", 0.0) < rules.get("laplacian_var_min", 0.0):
                suppress = True
            if row.get("lbp_high_ratio", 0.0) < rules.get("lbp_high_ratio_min", 0.0):
                suppress = True
            if suppress:
                predicted = "SANO"

        actual = row["actual"]
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
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "tn": tn, "fn": fn}


def main() -> None:
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f"Run extract_features.py first to create {FEATURES_PATH}")
    df = pd.read_csv(FEATURES_PATH)

    # Add lbp_high_ratio as proxy if missing
    if "lbp_high_ratio" not in df.columns:
        df["lbp_high_ratio"] = 0.0

    # Build candidate thresholds from percentiles of TP (ENFERMO where predicted ENFERMO)
    en_df = df[df["actual"] == "ENFERMO"]
    candidates = {}
    for feat in ["diameter_proxy", "hotspot_ratio", "color_variance", "laplacian_var", "lbp_high_ratio"]:
        vals = en_df.get(feat, pd.Series(dtype=float)).dropna()
        if len(vals) > 0:
            candidates[feat] = np.percentile(vals, [5, 10, 20, 30, 40])
        else:
            candidates[feat] = np.array([0.0])

    best = {"f1": -1.0}
    # Grid search
    for d in candidates["diameter_proxy"]:
        for h in candidates["hotspot_ratio"]:
            for c in candidates["color_variance"]:
                for l in candidates["laplacian_var"]:
                    for lbp in candidates["lbp_high_ratio"]:
                        rules = {
                            "diameter_proxy_min": float(d),
                            "hotspot_ratio_min": float(h),
                            "color_variance_min": float(c),
                            "laplacian_var_min": float(l),
                            "lbp_high_ratio_min": float(lbp),
                        }
                        stats = evaluate_thresholds(df, rules)
                        # enforce minimal recall
                        if stats["recall"] >= 0.65 and stats["f1"] > best["f1"]:
                            best = {**stats, **rules}

    if best["f1"] < 0:
        print("No candidate met recall constraint; relaxing to best F1")
        # pick best F1 ignoring recall
        best = {"f1": -1.0}
        for d in candidates["diameter_proxy"]:
            for h in candidates["hotspot_ratio"]:
                for c in candidates["color_variance"]:
                    for l in candidates["laplacian_var"]:
                        for lbp in candidates["lbp_high_ratio"]:
                            rules = {
                                "diameter_proxy_min": float(d),
                                "hotspot_ratio_min": float(h),
                                "color_variance_min": float(c),
                                "laplacian_var_min": float(l),
                                "lbp_high_ratio_min": float(lbp),
                            }
                            stats = evaluate_thresholds(df, rules)
                            if stats["f1"] > best["f1"]:
                                best = {**stats, **rules}

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(best, fh, indent=2)

    print("Saved tuned rules to", OUT_PATH)
    print(best)


if __name__ == "__main__":
    main()
