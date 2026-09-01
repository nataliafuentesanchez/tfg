# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Diagnostico detallado de falsos positivos en el benchmark HAM10000.
Identifica los patrones de features que llevan a clasificaciones incorrectas.
"""

import json
import os
import cv2
import numpy as np
from pathlib import Path
from app.services.inference_service import _compute_risk_score, analyze_image, PRIMARY_LABEL_THRESHOLD

# Rutas
IMAGES_DIR = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes"
METADATA_PATH = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/HAM10000_metadata.csv"

def load_metadata():
    """Carga el CSV de metadatos del HAM10000."""
    import csv
    metadata = {}
    try:
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_id = row.get('image_id')
                diagnosis = row.get('dx', '').lower().strip()
                metadata[image_id] = diagnosis
    except Exception as e:
        print(f"Error loading metadata: {e}")
    return metadata

def get_true_label(image_id: str, metadata: dict) -> str | None:
    """Retorna la etiqueta real (real diagnosis) del imagen."""
    diagnosis = metadata.get(image_id)
    if diagnosis in ['bcc', 'bkl', 'nv', 'vasc']:
        return 'SANO'
    elif diagnosis in ['akiec', 'df', 'mel']:
        return 'ENFERMO'
    return None

def analyze_image_with_features(image_path: str) -> tuple[str, float, dict]:
    """Analiza una imagen y retorna (primary_label, risk_score, features)."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, None, {}
        
        encoded = cv2.imencode('.jpg', image)[1].tobytes()
        result = analyze_image(encoded)
        
        score, features = _compute_risk_score(image)
        
        return result.primary_label, result.risk_score, features
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return None, None, {}

def diagnose_false_positives():
    """Ejecuta diagnostico de falsos positivos."""
    metadata = load_metadata()
    
    false_positives = []
    false_negatives = []
    
    total = 0
    processed = 0
    
    # Buscar todas las imágenes
    for part_dir in Path(IMAGES_DIR).glob("HAM10000_images_part_*"):
        for image_file in part_dir.glob("*.jpg"):
            total += 1
            image_id = image_file.stem
            true_label = get_true_label(image_id, metadata)
            
            if true_label is None:
                continue
            
            pred_label, risk_score, features = analyze_image_with_features(str(image_file))
            
            if pred_label is None:
                continue
            
            processed += 1
            
            # Detectar falsos positivos: predice ENFERMO pero es SANO
            if pred_label == "enfermo" and true_label == "SANO":
                false_positives.append({
                    "image_id": image_id,
                    "risk_score": risk_score,
                    "features": {k: float(v) for k, v in features.items()}
                })
            
            # Detectar falsos negativos: predice SANO pero es ENFERMO
            elif pred_label == "sano" and true_label == "ENFERMO":
                false_negatives.append({
                    "image_id": image_id,
                    "risk_score": risk_score,
                    "features": {k: float(v) for k, v in features.items()}
                })
    
    print(f"\nDIAGNOSIS RESULTS")
    print(f"Total images: {total}")
    print(f"Processed: {processed}")
    print(f"False Positives (SANO -> pred ENFERMO): {len(false_positives)}")
    print(f"False Negatives (ENFERMO -> pred SANO): {len(false_negatives)}")
    
    # Analizar patrones de FP
    if false_positives:
        print(f"\n=== FALSE POSITIVE PATTERNS (Sample of {min(5, len(false_positives))}) ===")
        for fp in sorted(false_positives, key=lambda x: x['risk_score'], reverse=True)[:5]:
            f = fp['features']
            print(f"\nImage: {fp['image_id']}, Score: {fp['risk_score']:.4f}")
            print(f"  diameter_proxy: {f.get('diameter_proxy', 0):.4f}")
            print(f"  asymmetry: {f.get('asymmetry', 0):.4f}")
            print(f"  mask_irregularity: {f.get('mask_irregularity', 0):.4f}")
            print(f"  edge_density: {f.get('edge_density', 0):.4f}")
            print(f"  contrast: {f.get('contrast', 0):.4f}")
            print(f"  hotspot_ratio: {f.get('hotspot_ratio', 0):.4f}")
            print(f"  color_variance: {f.get('color_variance', 0):.4f}")
            print(f"  red_mean: {f.get('red_mean', 0):.4f}")
            print(f"  red_hist_1: {f.get('red_hist_1', 0):.4f}")
            print(f"  red_hist_3: {f.get('red_hist_3', 0):.4f}")
    
    # Estadísticas agregadas de FP
    if false_positives:
        print(f"\n=== FALSE POSITIVE AGGREGATES ===")
        fp_features = {}
        for fp in false_positives:
            for k, v in fp['features'].items():
                if k not in fp_features:
                    fp_features[k] = []
                fp_features[k].append(v)
        
        for feature_name in ['diameter_proxy', 'asymmetry', 'mask_irregularity', 'edge_density', 
                             'contrast', 'hotspot_ratio', 'color_variance', 'red_mean', 'red_hist_1', 'red_hist_3']:
            if feature_name in fp_features:
                vals = fp_features[feature_name]
                print(f"{feature_name}:")
                print(f"  mean: {np.mean(vals):.4f}, median: {np.median(vals):.4f}, std: {np.std(vals):.4f}")
                print(f"  min: {np.min(vals):.4f}, max: {np.max(vals):.4f}")
    
    # Análisis de FN
    if false_negatives:
        print(f"\n=== FALSE NEGATIVE PATTERNS (Sample of {min(5, len(false_negatives))}) ===")
        for fn in sorted(false_negatives, key=lambda x: x['risk_score'])[:5]:
            f = fn['features']
            print(f"\nImage: {fn['image_id']}, Score: {fn['risk_score']:.4f}")
            print(f"  diameter_proxy: {f.get('diameter_proxy', 0):.4f}")
            print(f"  asymmetry: {f.get('asymmetry', 0):.4f}")
            print(f"  mask_irregularity: {f.get('mask_irregularity', 0):.4f}")
            print(f"  edge_density: {f.get('edge_density', 0):.4f}")
            print(f"  contrast: {f.get('contrast', 0):.4f}")
            print(f"  hotspot_ratio: {f.get('hotspot_ratio', 0):.4f}")
            print(f"  color_variance: {f.get('color_variance', 0):.4f}")
            print(f"  red_mean: {f.get('red_mean', 0):.4f}")
            print(f"  red_hist_1: {f.get('red_hist_1', 0):.4f}")
            print(f"  red_hist_3: {f.get('red_hist_3', 0):.4f}")

if __name__ == "__main__":
    diagnose_false_positives()
