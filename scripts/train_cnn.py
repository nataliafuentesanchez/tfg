# =============================================================================
# AnalisisImagenes - Entrenamiento de Red Neuronal Convolucional (ResNet-50/18)
# TFG Ingenieria de la Salud - Universidad de Malaga
# Autor: Natalia Fuentes Sanchez
# Dataset: HAM10000 (10.015 imagenes dermoscopicas)
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score, precision_score

# Mapeo de diagnosticos clinicos de HAM10000
DX_MAP = {
    'nv': 0,    # Nevus melanocitico (Benigno comun)
    'mel': 1,   # Melanoma (Maligno - Alta prioridad)
    'bkl': 2,   # Queratosis benigna (Benigno)
    'bcc': 3,   # Carcinoma basocelular (Maligno - Prioritario)
    'akiec': 4, # Queratosis actinica / Enf. Bowen (Premaligno/Maligno)
    'vasc': 5,  # Lesion vascular (Benigno)
    'df': 6     # Dermatofibroma (Benigno)
}

DX_NAMES = ['nv (Nevus)', 'mel (Melanoma)', 'bkl (Queratosis Benigna)', 
            'bcc (Carcinoma Basocelular)', 'akiec (Queratosis Actinica)', 
            'vasc (Vascular)', 'df (Dermatofibroma)']

MALIGNANT_CLASSES = {'mel', 'bcc', 'akiec'}

class HAM10000Dataset(Dataset):
    def __init__(self, df: pd.DataFrame, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['image_path']
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        label = row['label']
        return image, label


def find_image_path(image_id: str, image_dirs: list) -> str:
    filename = f"{image_id}.jpg"
    for d in image_dirs:
        candidate = os.path.join(d, filename)
        if os.path.exists(candidate):
            return candidate
    return None


def prepare_data(data_dir: str, image_dirs: list, extra_melanoma_dir: str = None, max_extra_mel: int = 2000):
    metadata_path = os.path.join(data_dir, "HAM10000_metadata.csv")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"No se encontro el archivo de metadatos en: {metadata_path}")
    
    df = pd.read_csv(metadata_path)
    print(f"[1/5] Metadatos cargados: {len(df)} registros.")
    
    # Localizar rutas reales de las imagenes
    df['image_path'] = df['image_id'].apply(lambda x: find_image_path(x, image_dirs))
    missing = df['image_path'].isna().sum()
    if missing > 0:
        print(f"Advertencia: {missing} imagenes no encontradas en disco. Filtrando...")
        df = df.dropna(subset=['image_path'])
    print(f"Total imagenes validas en disco: {len(df)}")
    
    # Asignar etiquetas numericas
    df['label'] = df['dx'].map(DX_MAP)
    df['is_malignant'] = df['dx'].apply(lambda x: 1 if x in MALIGNANT_CLASSES else 0)
    
    # Division por lesion_id para evitar fuga de datos (data leakage de la misma lesion)
    gss1 = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
    train_idx, temp_idx = next(gss1.split(df, groups=df['lesion_id']))
    
    train_df = df.iloc[train_idx].copy()
    temp_df = df.iloc[temp_idx].copy()
    
    gss2 = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
    val_idx, test_idx = next(gss2.split(temp_df, groups=temp_df['lesion_id']))
    
    val_df = temp_df.iloc[val_idx].copy()
    test_df = temp_df.iloc[test_idx].copy()
    
    # Inyeccion selectiva de melanomas adicionales en train_df (sin tocar val ni test)
    if extra_melanoma_dir and os.path.exists(extra_melanoma_dir):
        import glob
        extra_files = glob.glob(os.path.join(extra_melanoma_dir, "*.jpg"))
        if extra_files:
            extra_files = sorted(extra_files)[:max_extra_mel]
            print(f"[1.5/5] Inyectando {len(extra_files)} melanomas adicionales en TRAIN desde {extra_melanoma_dir}...")
            extra_rows = []
            for i, p in enumerate(extra_files):
                img_id = os.path.splitext(os.path.basename(p))[0]
                extra_rows.append({
                    'lesion_id': f'EXTRA_MEL_{i:05d}',
                    'image_id': img_id,
                    'dx': 'mel',
                    'dx_type': 'histo',
                    'age': 50.0,
                    'sex': 'unknown',
                    'localization': 'unknown',
                    'image_path': p,
                    'label': DX_MAP['mel'],
                    'is_malignant': 1
                })
            extra_df = pd.DataFrame(extra_rows)
            train_df = pd.concat([train_df, extra_df], ignore_index=True)
            print(f"✓ Train enriquecido: nuevo tamaño={len(train_df)} (Melanomas en train={sum(train_df['dx']=='mel')})")

    print(f"[2/5] Particion de datos: Train={len(train_df)} | Val={len(val_df)} | Test={len(test_df)}")
    return train_df, val_df, test_df


def get_transforms():
    # Normalizacion estandar ImageNet
    norm_mean = [0.485, 0.456, 0.406]
    norm_std = [0.229, 0.224, 0.225]
    
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(norm_mean, norm_std)
    ])
    
    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(norm_mean, norm_std)
    ])
    
    return train_transform, eval_transform


def build_model(num_classes=7, architecture="resnet50"):
    """
    Construye la red neuronal con pesos preentrenados en ImageNet.
    - resnet50 (por defecto): Mejor capacidad de representacion, nativo en MPS, sin OOM.
    - resnet18: Baseline ligero del proyecto.
    """
    if architecture == "resnet50":
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    elif architecture == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    else:
        raise ValueError(f"Arquitectura no soportada: {architecture}")

    in_features = model.fc.in_features
    # Dropout 0.4 para resnet50 (mas parametros, mayor riesgo de sobreajuste)
    dropout_rate = 0.4 if architecture == "resnet50" else 0.3
    model.fc = nn.Sequential(
        nn.Dropout(dropout_rate),
        nn.Linear(in_features, num_classes)
    )
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        
    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    total = len(all_labels)
    epoch_loss = running_loss / total
    epoch_acc = np.mean(np.array(all_preds) == np.array(all_labels))
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    
    return epoch_loss, epoch_acc, macro_f1, all_preds, all_labels


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento ResNet-50/18 sobre HAM10000")
    parser.add_argument("--epochs", type=int, default=10, help="Numero de epocas")
    parser.add_argument("--batch_size", type=int, default=16, help="Tamano del lote (16 recomendado en Apple MPS)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--architecture", type=str, default="resnet18", choices=["resnet18", "resnet50"], help="Arquitectura CNN")
    parser.add_argument("--label_smoothing", type=float, default=0.0, help="Label smoothing para CrossEntropyLoss (0=desactivado)")
    parser.add_argument("--extra_melanoma_dir", type=str, default="/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/melanoma_cancer_dataset/train/malignant", help="Directorio con melanomas adicionales para train")
    parser.add_argument("--max_extra_mel", type=int, default=2000, help="Maximo numero de melanomas adicionales a inyectar")
    args = parser.parse_args()
    
    base_data_dir = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos"
    image_dirs = [
        os.path.join(base_data_dir, "imagenes", "HAM10000_images_part_1"),
        os.path.join(base_data_dir, "imagenes", "HAM10000_images_part_2")
    ]
    
    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Dispositivo de computo seleccionado: {device}")
    print(f"Arquitectura: {args.architecture} | LR: {args.lr} | Batch: {args.batch_size} | Label Smoothing: {args.label_smoothing}")
    print(f"Melanomas adicionales: {args.extra_melanoma_dir} (max: {args.max_extra_mel})")
    
    train_df, val_df, test_df = prepare_data(
        base_data_dir, 
        image_dirs, 
        extra_melanoma_dir=args.extra_melanoma_dir, 
        max_extra_mel=args.max_extra_mel
    )
    train_tf, eval_tf = get_transforms()
    
    train_ds = HAM10000Dataset(train_df, transform=train_tf)
    val_ds = HAM10000Dataset(val_df, transform=eval_tf)
    test_ds = HAM10000Dataset(test_df, transform=eval_tf)
    
    # num_workers=0 en macOS/MPS evita los errores de MallocStackLogging y garantiza estabilidad
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    # Calcular pesos ponderados para balancear clases en la funcion de perdida
    class_counts = train_df['label'].value_counts().sort_index().values
    class_weights = 1.0 / (class_counts + 1e-5)
    class_weights = class_weights / class_weights.sum() * len(class_counts)
    weight_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)
    
    print(f"[3/5] CrossEntropyLoss con pesos de balanceo y label_smoothing={args.label_smoothing}.")
    criterion = nn.CrossEntropyLoss(weight=weight_tensor, label_smoothing=args.label_smoothing)
    
    model = build_model(num_classes=7, architecture=args.architecture).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    
    os.makedirs("models", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    best_val_f1 = 0.0
    best_model_path = "models/best_skin_cnn.pth"
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': [], 'val_f1': []}
    
    print(f"\n[4/5] Iniciando entrenamiento ({args.epochs} epocas)...")
    start_time = time.time()
    
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_f1, _, _ = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_f1'].append(val_f1)
        
        elapsed = time.time() - t0
        print(f"Epoca [{epoch:02d}/{args.epochs:02d}] ({elapsed:.1f}s) | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.1f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.1f}% F1: {val_f1:.4f}")
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save({
                'epoch': epoch,
                'architecture': args.architecture,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_f1': val_f1,
                'dx_map': DX_MAP,
                'dx_names': DX_NAMES
            }, best_model_path)
            print(f"  --> Mejor modelo guardado en '{best_model_path}' (Val Macro F1: {val_f1:.4f})")
            
    total_time = time.time() - start_time
    print(f"\nEntrenamiento completado en {total_time/60:.2f} minutos.")
    
    # [5/5] Evaluacion en el conjunto Test
    print("\n[5/5] Evaluando en Test Set con el mejor modelo...")
    checkpoint = torch.load(best_model_path, map_location=device, weights_only=False)
    saved_arch = checkpoint.get('architecture', args.architecture)
    model = build_model(num_classes=7, architecture=saved_arch).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_acc, test_f1, test_preds, test_labels = evaluate(model, test_loader, criterion, device)
    print(f"\nResultados finales en Test Set:")
    print(f"Accuracy: {test_acc*100:.2f}% | Macro F1: {test_f1:.4f}")
    
    report = classification_report(test_labels, test_preds, target_names=DX_NAMES, digits=4)
    print("\nReporte Clinico de Clasificacion:")
    print(report)
    
    with open("docs/cnn_evaluation_report.txt", "w") as f:
        f.write(f"Evaluacion {saved_arch.upper()} HAM10000\nFecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Test Accuracy: {test_acc*100:.2f}%\nTest Macro F1: {test_f1:.4f}\n\n")
        f.write(report)
        
    # Guardar metadatos de las clases para la API
    classes_meta = {
        'architecture': saved_arch,
        'dx_map': DX_MAP,
        'dx_names': DX_NAMES,
        'malignant_classes': list(MALIGNANT_CLASSES),
        'test_accuracy': float(test_acc),
        'test_macro_f1': float(test_f1)
    }
    with open("models/cnn_classes.json", "w") as f:
        json.dump(classes_meta, f, indent=2)
        
    # Generar graficos para la memoria del TFG
    # 1. Matriz de Confusion
    cm = confusion_matrix(test_labels, test_preds)
    plt.figure(figsize=(9, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[n.split()[0] for n in DX_NAMES],
                yticklabels=[n.split()[0] for n in DX_NAMES])
    plt.title(f"Matriz de Confusion - {saved_arch.upper()} (HAM10000 Test Set)", fontsize=13, pad=12)
    plt.xlabel("Prediccion del Modelo", fontsize=11)
    plt.ylabel("Diagnostico Real (Ground Truth)", fontsize=11)
    plt.tight_layout()
    plt.savefig("docs/confusion_matrix_cnn.png", dpi=300)
    plt.close()
    print("Grafico guardado: docs/confusion_matrix_cnn.png")
    
    # 2. Curvas de Aprendizaje
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss', color='#2b5c8f', lw=2)
    plt.plot(history['val_loss'], label='Val Loss', color='#d9534f', lw=2)
    plt.title("Curva de Perdida (Loss)", fontsize=12)
    plt.xlabel("Epoca")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.subplot(1, 2, 2)
    plt.plot([a*100 for a in history['train_acc']], label='Train Acc (%)', color='#2b5c8f', lw=2)
    plt.plot([a*100 for a in history['val_acc']], label='Val Acc (%)', color='#5cb85c', lw=2)
    plt.title("Curva de Precision (Accuracy)", fontsize=12)
    plt.xlabel("Epoca")
    plt.ylabel("Accuracy (%)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig("docs/training_curves_cnn.png", dpi=300)
    plt.close()
    print("Grafico guardado: docs/training_curves_cnn.png")
    print("\nProceso finalizado con exito. El modelo esta listo para ser integrado en la app.")

if __name__ == "__main__":
    main()
