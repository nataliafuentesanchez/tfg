# =============================================================================
# AnalisisImagenes - Evaluacion de ResNet-18 en Test Set y Generacion de Graficos TFG
# =============================================================================

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score

from scripts.train_cnn import (
    HAM10000Dataset, prepare_data, get_transforms, build_model, 
    evaluate, DX_MAP, DX_NAMES, MALIGNANT_CLASSES
)

def main():
    base_data_dir = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos"
    image_dirs = [
        os.path.join(base_data_dir, "imagenes", "HAM10000_images_part_1"),
        os.path.join(base_data_dir, "imagenes", "HAM10000_images_part_2")
    ]
    
    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Dispositivo de evaluacion: {device}")
    
    _, _, test_df = prepare_data(base_data_dir, image_dirs)
    _, eval_tf = get_transforms()
    test_ds = HAM10000Dataset(test_df, transform=eval_tf)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=2)
    
    best_model_path = "models/best_skin_cnn.pth"
    if not os.path.exists(best_model_path):
        print(f"Error: {best_model_path} no existe.")
        return
        
    print(f"Cargando modelo desde {best_model_path}...")
    checkpoint = torch.load(best_model_path, map_location=device, weights_only=False)
    
    model = build_model(num_classes=7).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    criterion = nn.CrossEntropyLoss()
    test_loss, test_acc, test_f1, test_preds, test_labels = evaluate(model, test_loader, criterion, device)
    
    print(f"\n=======================================================")
    print(f"📊 RESULTADOS FINALES EN TEST SET (1.494 imagenes no vistas)")
    print(f"=======================================================")
    print(f"Precisión Global (Accuracy): {test_acc*100:.2f}%")
    print(f"Macro F1-Score:              {test_f1:.4f}")
    
    report = classification_report(test_labels, test_preds, target_names=DX_NAMES, digits=4)
    print("\nReporte Clinico por Patologia:")
    print(report)
    
    os.makedirs("docs", exist_ok=True)
    with open("docs/cnn_evaluation_report.txt", "w") as f:
        f.write(f"Evaluacion Clinica ResNet-18 HAM10000 (Test Set)\n")
        f.write(f"Accuracy Global: {test_acc*100:.2f}%\n")
        f.write(f"Macro F1-Score: {test_f1:.4f}\n\n")
        f.write(report)
        
    # Guardar metadatos JSON para la API
    classes_meta = {
        'dx_map': DX_MAP,
        'dx_names': DX_NAMES,
        'malignant_classes': list(MALIGNANT_CLASSES),
        'test_accuracy': float(test_acc),
        'test_macro_f1': float(test_f1)
    }
    with open("models/cnn_classes.json", "w") as f:
        json.dump(classes_meta, f, indent=2)
        
    # 1. Matriz de Confusion
    cm = confusion_matrix(test_labels, test_preds)
    plt.figure(figsize=(9, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[n.split()[0] for n in DX_NAMES],
                yticklabels=[n.split()[0] for n in DX_NAMES])
    plt.title("Matriz de Confusion - ResNet-18 (HAM10000 Test Set)", fontsize=13, pad=12)
    plt.xlabel("Prediccion del Modelo", fontsize=11)
    plt.ylabel("Diagnostico Real (Ground Truth)", fontsize=11)
    plt.tight_layout()
    plt.savefig("docs/confusion_matrix_cnn.png", dpi=300)
    plt.close()
    print("✓ Matriz de confusion guardada en: docs/confusion_matrix_cnn.png")
    
    # 2. Resumen Triage Binario (Sano vs Sospechoso/Maligno)
    malignant_idx = [DX_MAP[k] for k in MALIGNANT_CLASSES]
    bin_labels = [1 if y in malignant_idx else 0 for y in test_labels]
    bin_preds = [1 if p in malignant_idx else 0 for p in test_preds]
    
    bin_report = classification_report(bin_labels, bin_preds, target_names=['Benigno / Seguimiento', 'Maligno / Derivacion'], digits=4)
    print("\n-------------------------------------------------------")
    print("🩺 TRIAGE CLINICO BINARIO (Derivacion vs Seguimiento):")
    print(bin_report)
    print("-------------------------------------------------------")

if __name__ == "__main__":
    main()
