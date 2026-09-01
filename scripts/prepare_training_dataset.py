# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Prepara el dataset de entrenamiento extrayendo features de todas las imágenes HAM10000.
Genera un CSV con features + labels para entrenar modelos supervisados.
"""

import csv
import os
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from app.services.inference_service import _compute_risk_score

# Rutas
IMAGES_DIR = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes"
METADATA_PATH = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/HAM10000_metadata.csv"
OUTPUT_PATH = "./models/training_features.csv"

def load_metadata():
    """Carga el CSV de metadatos del HAM10000."""
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

def get_true_label(image_id: str, metadata: dict) -> int | None:
    """Retorna 1 si ENFERMO, 0 si SANO, None si desconocido."""
    diagnosis = metadata.get(image_id)
    if diagnosis in ['bcc', 'bkl', 'nv', 'vasc']:
        return 0  # SANO
    elif diagnosis in ['akiec', 'df', 'mel']:
        return 1  # ENFERMO
    return None

def extract_features_from_image(image_path: str) -> dict | None:
    """Extrae features de una imagen usando _compute_risk_score."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        score, features = _compute_risk_score(image)
        features['risk_score'] = score
        return features
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return None

def prepare_dataset():
    """Prepara el dataset completo de features + labels."""
    metadata = load_metadata()
    
    rows = []
    processed = 0
    skipped = 0
    
    print("Extrayendo features de todas las imágenes...")
    
    # Buscar todas las imágenes
    for part_dir in sorted(Path(IMAGES_DIR).glob("HAM10000_images_part_*")):
        for image_file in sorted(part_dir.glob("*.jpg")):
            image_id = image_file.stem
            true_label = get_true_label(image_id, metadata)
            
            if true_label is None:
                skipped += 1
                continue
            
            features = extract_features_from_image(str(image_file))
            
            if features is None:
                skipped += 1
                continue
            
            # Agregar label y metadata
            features['image_id'] = image_id
            features['true_label'] = true_label
            rows.append(features)
            
            processed += 1
            if processed % 500 == 0:
                print(f"  Procesadas {processed} imágenes...")
    
    print(f"\nTotal procesadas: {processed}, Skipped: {skipped}")
    
    # Convertir a DataFrame
    df = pd.DataFrame(rows)
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
    
    # Guardar CSV
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nDataset guardado en {OUTPUT_PATH}")
    print(f"Dimensiones: {df.shape}")
    print(f"\nDistribución de labels:")
    print(df['true_label'].value_counts())
    print(f"\nPrimeras 5 filas:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    prepare_dataset()
