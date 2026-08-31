"""Entrena un clasificador logístico simple en NumPy como filtro de falsos positivos.
Guarda pesos y normalización en models/filter_numpy.npz
"""
from __future__ import annotations

import csv
from pathlib import Path
import numpy as np
import math

FEATURES_PATH = Path.cwd() / "models" / "features.csv"
OUT_PATH = Path.cwd() / "models" / "filter_numpy.npz"


def load_features() -> tuple[np.ndarray, np.ndarray, list[str]]:
    import pandas as pd

    df = pd.read_csv(FEATURES_PATH)
    # select feature columns used previously
    feature_cols = [
        "red_mean",
        "hotspot_ratio",
        "diameter_proxy",
        "asymmetry",
        "color_variance",
        "edge_density",
        "texture_variation",
        "laplacian_var",
        "hsv_mean",
        "hsv_std",
        "red_hist_0",
        "red_hist_1",
        "red_hist_2",
        "red_hist_3",
    ]
    # fill missing columns with zeros
    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0.0
    X = df[feature_cols].to_numpy(dtype=float)
    y = (df["actual"] == "ENFERMO").astype(int).to_numpy()
    return X, y, feature_cols


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


def train(X: np.ndarray, y: np.ndarray, lr=0.1, epochs=2000, reg=1e-4) -> tuple[np.ndarray, float]:
    n_samples, n_features = X.shape
    # normalize
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-9
    Xn = (X - mean) / std

    # add bias
    Xb = np.hstack([np.ones((n_samples, 1)), Xn])
    w = np.zeros(Xb.shape[1])

    # simple gradient descent with class weighting
    pos = y.sum()
    neg = n_samples - pos
    pos_w = 0.5 / (pos / n_samples) if pos > 0 else 1.0
    neg_w = 0.5 / (neg / n_samples) if neg > 0 else 1.0
    weights = np.where(y == 1, pos_w, neg_w)

    for epoch in range(epochs):
        z = Xb.dot(w)
        p = sigmoid(z)
        error = p - y
        grad = (Xb * (error * weights)[:, None]).mean(axis=0) + reg * np.r_[0.0, w[1:]]
        w -= lr * grad
        if epoch % 500 == 0:
            preds = (p >= 0.5).astype(int)
            acc = (preds == y).mean()
            print(f"epoch {epoch} acc={acc:.4f}")

    return w, mean, std


def main() -> None:
    X, y, cols = load_features()
    w, mean, std = train(X, y, lr=0.1, epochs=2000)
    OUT_PATH.parent.mkdir(exist_ok=True)
    np.savez(OUT_PATH, w=w, mean=mean, std=std, cols=np.array(cols))
    print("Saved numpy logreg model to", OUT_PATH)


if __name__ == "__main__":
    main()
