
# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""Diagnóstico de probabilidades del modelo supervisado."""

import cv2
import numpy as np
from app.services.inference_service import _compute_risk_score, _load_supervised_model, _load_scaler

# Test on a few images
test_images = [
    ("/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1/ISIC_0024306.jpg", "SANO"),
    ("/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1/ISIC_0024310.jpg", "ENFERMO"),
]

model = _load_supervised_model()
scaler = _load_scaler()

feature_order = ['red_mean', 'contrast', 'hotspot_ratio', 'edge_density', 
                 'asymmetry', 'color_variance', 'diameter_proxy', 'mask_irregularity', 
                 'texture_variation', 'laplacian_var', 'hsv_mean', 'hsv_std', 
                 'red_hist_0', 'red_hist_1', 'red_hist_2', 'red_hist_3', 'risk_score']

for img_path, true_label in test_images:
    img = cv2.imread(img_path)
    score, feats = _compute_risk_score(img)
    
    fvec = np.array([feats.get(f, score if f == 'risk_score' else 0.0) for f in feature_order]).reshape(1, -1)
    fvec_scaled = scaler.transform(fvec)
    
    pred = model.predict(fvec_scaled)[0]
    proba = model.predict_proba(fvec_scaled)[0]
    
    print(f"Image: {img_path.split('/')[-1]}")
    print(f"  True label: {true_label}")
    print(f"  Heuristic score: {score:.4f}")
    print(f"  Supervised pred: {pred} (0=sano, 1=enfermo)")
    print(f"  Proba[sano]: {proba[0]:.4f}, Proba[enfermo]: {proba[1]:.4f}")
    print(f"  Condition (proba[0] > 0.65 and score < 0.75): {proba[0] > 0.65 and score < 0.75}")
    print()
