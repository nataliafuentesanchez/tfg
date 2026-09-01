# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Entrena un modelo supervisado (LogisticRegression + RandomForest)
sobre las features extraídas del HAM10000.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    precision_recall_fscore_support, roc_auc_score
)
import joblib
import os

# Rutas
FEATURES_PATH = "./models/training_features.csv"
MODEL_OUTPUT_PATH = "./models/supervised_model.joblib"
SCALER_OUTPUT_PATH = "./models/supervised_scaler.joblib"

def train_models():
    """Entrena modelos de clasificación supervisada."""
    
    # Cargar dataset
    print("Cargando dataset...")
    df = pd.read_csv(FEATURES_PATH)
    
    # Separar features y label
    X = df.drop(['image_id', 'true_label'], axis=1)
    y = df['true_label']
    
    print(f"Features: {X.shape}")
    print(f"Labels: {y.value_counts().to_dict()}")
    
    # División train/val/test (70/15/15)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_test, y_test, test_size=0.50, random_state=42, stratify=y_test
    )
    
    print(f"\nTrain: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
    
    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # ===== LOGISTIC REGRESSION =====
    print("\n=== LOGISTIC REGRESSION ===")
    lr_model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    
    y_val_pred = lr_model.predict(X_val_scaled)
    y_test_pred = lr_model.predict(X_test_scaled)
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='weighted')
    print(f"Test Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    print("\nClassification Report (Test):")
    print(classification_report(y_test, y_test_pred, target_names=['SANO', 'ENFERMO']))
    
    # ===== RANDOM FOREST =====
    print("\n=== RANDOM FOREST ===")
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    y_val_pred_rf = rf_model.predict(X_val)
    y_test_pred_rf = rf_model.predict(X_test)
    
    precision_rf, recall_rf, f1_rf, _ = precision_recall_fscore_support(y_test, y_test_pred_rf, average='weighted')
    print(f"Test Precision: {precision_rf:.4f}, Recall: {recall_rf:.4f}, F1: {f1_rf:.4f}")
    print("\nClassification Report (Test):")
    print(classification_report(y_test, y_test_pred_rf, target_names=['SANO', 'ENFERMO']))
    
    # ===== FEATURE IMPORTANCE (RF) =====
    print("\n=== FEATURE IMPORTANCE (Random Forest) ===")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance.head(10))
    
    # Guardar el mejor modelo (RF tiene mejor F1 generalmente)
    print("\nGuardando modelos...")
    os.makedirs("./models", exist_ok=True)
    joblib.dump(rf_model, MODEL_OUTPUT_PATH)
    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print(f"Modelo guardado: {MODEL_OUTPUT_PATH}")
    print(f"Scaler guardado: {SCALER_OUTPUT_PATH}")
    
    # Resumen final
    print("\n=== RESUMEN FINAL ===")
    print(f"LogisticRegression Test F1: {f1:.4f}")
    print(f"RandomForest Test F1: {f1_rf:.4f}")
    print(f"Mejor modelo: RandomForest" if f1_rf > f1 else "Mejor modelo: LogisticRegression")

if __name__ == "__main__":
    train_models()
