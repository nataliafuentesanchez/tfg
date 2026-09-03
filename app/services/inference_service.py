# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

import os
import json
from io import BytesIO
from typing import Optional, Dict, Any

import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms, models

from app.schemas.prediction import AnalysisResponse

# Configuracion de modelo CNN y rutas
_MODEL_PATH = os.path.join(os.getcwd(), "models", "best_skin_cnn.pth")
_CLASSES_PATH = os.path.join(os.getcwd(), "models", "cnn_classes.json")

_cnn_model = None
_cnn_device = None
_cnn_classes_info = None

DIAGNOSIS_LABELS = {
    "nv": "Nevus Melanocítico (Lunar común benigno)",
    "mel": "Melanoma (Lesión maligna sospechosa)",
    "bkl": "Queratosis Benigna (Lesión seborreica/solar)",
    "bcc": "Carcinoma Basocelular (Neoplasia maligna)",
    "akiec": "Queratosis Actínica / Enf. Bowen (Lesión premaligna)",
    "vasc": "Lesión Vascular (Angioma o similar, benigno)",
    "df": "Dermatofibroma (Nódulo cutáneo benigno)",
}

MALIGNANT_CLASSES = {"mel", "bcc", "akiec"}
URGENT_REFERRAL_THRESHOLD = 0.40

# Transformaciones con Resize y CenterCrop para fotos de cualquier origen y resolucion
_eval_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _load_cnn_model():
    """Carga en memoria la red neuronal ResNet-18 entrenada en HAM10000."""
    global _cnn_model, _cnn_device, _cnn_classes_info
    if _cnn_model is not None:
        return _cnn_model, _cnn_device, _cnn_classes_info

    if not os.path.exists(_MODEL_PATH):
        return None, None, None

    try:
        _cnn_device = torch.device(
            "mps" if torch.backends.mps.is_available() 
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        
        model = models.resnet18(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 7)
        )
        
        checkpoint = torch.load(_MODEL_PATH, map_location=_cnn_device, weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(_cnn_device)
        model.eval()
        _cnn_model = model

        if os.path.exists(_CLASSES_PATH):
            with open(_CLASSES_PATH, "r", encoding="utf-8") as f:
                _cnn_classes_info = json.load(f)

        return _cnn_model, _cnn_device, _cnn_classes_info
    except Exception as e:
        print(f"Aviso: no se pudo cargar la red neuronal: {e}")
        return None, None, None


def _decode_image(content: bytes) -> np.ndarray:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Formato de imagen no valido o archivo corrupto.")
    return image


def _extract_abcde_features(image: np.ndarray) -> Dict[str, Any]:
    """
    Modulo descriptor ABCDE para Interpretabilidad Clinica (Explainable AI - XAI):
    - A (Asimetria): Solapamiento bilateral horizontal y vertical.
    - B (Borde): Indice de irregularidad perimetral.
    - C (Color): Variabilidad cromatica y presencia de policromatismo/hotspots.
    - D (Diametro): Estimacion de proporcion de area.
    - E (Evolucion / Estructura): Textura diferencial y varianza laplaciana.
    """
    resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

    # Segmentacion robusta hibrida (Otsu para pigmento oscuro + distancia de color para rojas)
    _, otsu_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    red_channel = rgb[:, :, 0].astype(np.float32)
    green_channel = rgb[:, :, 1].astype(np.float32)
    blue_channel = rgb[:, :, 2].astype(np.float32)
    
    color_dist = np.sqrt(
        (red_channel - float(np.median(red_channel))) ** 2
        + (green_channel - float(np.median(green_channel))) ** 2
        + (blue_channel - float(np.median(blue_channel))) ** 2
    )
    chroma_mask = (color_dist > 25).astype(np.uint8) * 255

    lesion_mask = cv2.bitwise_or(otsu_mask, chroma_mask)
    kernel = np.ones((5, 5), dtype=np.uint8)
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_OPEN, kernel)
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_CLOSE, kernel)

    # 1. B - Borde y D - Diametro
    contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 25]
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        irregularity = (perimeter ** 2) / (4 * np.pi * area + 1e-6)
        border_irregularity = float(np.clip((irregularity - 1.0) / 3.0, 0.0, 1.0))
        diameter_proxy = float(min(1.0, area / (224 * 224 * 0.10)))
    else:
        border_irregularity = 0.0
        diameter_proxy = 0.0

    # 2. A - Asimetria (horizontal y vertical)
    if lesion_mask.sum() > 0:
        flipped_h = np.fliplr(lesion_mask)
        flipped_v = np.flipud(lesion_mask)
        mask_pixels = float((lesion_mask > 0).sum())
        overlap_h = float(np.logical_and(lesion_mask > 0, flipped_h > 0).sum()) / max(1.0, mask_pixels)
        overlap_v = float(np.logical_and(lesion_mask > 0, flipped_v > 0).sum()) / max(1.0, mask_pixels)
        asymmetry = float(np.clip(1.0 - min(overlap_h, overlap_v), 0.0, 1.0))
    else:
        asymmetry = 0.0

    # 3. C - Color
    color_variance = float(np.std(rgb[lesion_mask > 0], axis=0).mean() / 255.0) if lesion_mask.sum() > 0 else 0.0
    color_heterogeneity = float(np.clip(color_variance * 3.5, 0.0, 1.0))

    # 4. E - Estructura y Textura
    edge_density = float(np.mean(cv2.Canny(gray, 40, 120) > 0))
    laplacian_var = float(np.var(cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)))
    structure_complexity = float(np.clip(edge_density * 4.0 + min(1.0, laplacian_var / 600.0), 0.0, 1.0))

    # Descripciones cualitativas
    a_desc = "Asimetría marcada (alta sospecha)" if asymmetry > 0.30 else ("Asimetría leve/moderada" if asymmetry > 0.15 else "Simétrica (patrón regular)")
    b_desc = "Bordes irregulares o poco definidos" if border_irregularity > 0.25 else "Bordes regulares y circunscritos"
    c_desc = "Heterogeneidad cromática (múltiples tonos)" if color_heterogeneity > 0.25 else "Coloración homogénea"
    d_desc = "Diámetro significativo (> 6mm est.)" if diameter_proxy > 0.35 else "Diámetro focal/pequeño"
    e_desc = "Estructura interna atípica" if structure_complexity > 0.30 else "Estructura uniforme"

    return {
        "asymmetry_score": round(asymmetry, 3),
        "asymmetry_desc": a_desc,
        "border_score": round(border_irregularity, 3),
        "border_desc": b_desc,
        "color_score": round(color_heterogeneity, 3),
        "color_desc": c_desc,
        "diameter_score": round(diameter_proxy, 3),
        "diameter_desc": d_desc,
        "structure_score": round(structure_complexity, 3),
        "structure_desc": e_desc,
    }


def _human_primary_label(label: str) -> str:
    return "Sano" if label == "sano" else "Enfermo"


def _human_benign_malignant(label: str) -> str:
    return "Benigno probable" if label == "benigno_probable" else "Maligno probable"


def _build_user_report(
    primary_label: str,
    severity: str,
    benign_malignant: str,
    risk_score: float,
    likely_cause: str,
    recommendation: str,
    abcde: Dict[str, Any]
) -> str:
    risk_percent = round(risk_score * 100, 1)
    return (
        f"Resultado principal: {_human_primary_label(primary_label)}. "
        f"Nivel de gravedad estimado: {severity.upper()}. "
        f"Clasificacion de lesion: {_human_benign_malignant(benign_malignant)}. "
        f"Riesgo de malignidad estimado: {risk_percent}%. "
        f"Patologia mas compatible: {likely_cause}. "
        f"Evaluacion ABCDE: "
        f"[A: {abcde['asymmetry_desc']}; "
        f"B: {abcde['border_desc']}; "
        f"C: {abcde['color_desc']}; "
        f"D: {abcde['diameter_desc']}]. "
        f"Recomendacion clinica: {recommendation}"
    )


def _predict_with_cnn(content: bytes) -> tuple[float, str, dict[str, float], str]:
    """Ejecuta inferencia mediante la red neuronal convolucional ResNet-18."""
    model, device, _ = _load_cnn_model()
    if model is None:
        raise RuntimeError("Modelo CNN no disponible.")

    pil_image = Image.open(BytesIO(content)).convert("RGB")
    tensor = _eval_transform(pil_image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    dx_idx_to_name = {
        0: "nv", 1: "mel", 2: "bkl", 3: "bcc", 
        4: "akiec", 5: "vasc", 6: "df"
    }

    prob_dict = {dx_idx_to_name[i]: float(prob) for i, prob in enumerate(probabilities)}
    
    # Riesgo de patologias malignas/sospechosas (MEL + BCC + AKIEC)
    malignant_risk = prob_dict["mel"] + prob_dict["bcc"] + prob_dict["akiec"]
    
    top_dx = max(prob_dict, key=prob_dict.get)
    top_label_human = DIAGNOSIS_LABELS.get(top_dx, top_dx)
    
    return float(malignant_risk), top_label_human, prob_dict, top_dx


def analyze_image(content: bytes, filename: str | None = None) -> AnalysisResponse:
    image = _decode_image(content)
    # Extraccion de criterios clinicos ABCDE
    abcde_features = _extract_abcde_features(image)

    # 1. Inferencia con la Red Neuronal (ResNet-18)
    model, _, _ = _load_cnn_model()
    if model is not None:
        try:
            malignant_risk, top_label, probs, top_dx = _predict_with_cnn(content)
            mel_prob = probs.get("mel", 0.0)
            bcc_prob = probs.get("bcc", 0.0)
            akiec_prob = probs.get("akiec", 0.0)

            # Marcadores de sospecha oncologica
            abcde_is_atypical = (
                abcde_features["asymmetry_score"] >= 0.28
                or abcde_features["border_score"] >= 0.25
                or abcde_features["color_score"] >= 0.25
            )

            # Si el modelo predice melanoma o maligno, o si el riesgo de malignidad supera el 18%,
            # o si hay sospecha morfologica ABCDE combinada con probabilidad residual de melanoma (> 8%):
            is_malignant_alert = (
                top_dx in MALIGNANT_CLASSES
                or malignant_risk >= 0.18
                or mel_prob >= 0.08
                or (abcde_is_atypical and malignant_risk >= 0.12)
            )

            if is_malignant_alert:
                primary_label = "enfermo"
                benign_malignant = "maligno_probable"
                severity = "peligro"
                referral = True
                
                # Riesgo clinico calibrado para alerta oncologica
                effective_risk = max(0.78, min(0.98, malignant_risk * 3.5))

                if top_dx == "mel" or mel_prob >= 0.10:
                    likely_cause = "Melanoma (Neoplasia Maligna Sospechosa - Alta Prioridad)"
                elif top_dx == "bcc" or bcc_prob >= 0.10:
                    likely_cause = "Carcinoma Basocelular (Neoplasia Maligna)"
                elif top_dx == "akiec" or akiec_prob >= 0.10:
                    likely_cause = "Queratosis Actínica / Enf. Bowen (Lesión Premaligna)"
                else:
                    likely_cause = "Lesión Pigmentada Atípica con Criterios de Riesgo Maligno"

                recommendation = "Derivación prioritaria e inmediata al dermatólogo para biopsia y evaluación clínica urgente."
            else:
                primary_label = "sano"
                benign_malignant = "benigno_probable"
                severity = "ninguno" if malignant_risk < 0.08 else "bajo"
                referral = False
                effective_risk = min(0.15, malignant_risk)
                likely_cause = f"{top_label} (Patrón Benigno Frecuente)"
                recommendation = "No se aprecian signos de malignidad inmediata; mantener autoexploración periódica."

            return AnalysisResponse(
                filename=filename or "imagen_subida",
                primary_label=primary_label,
                severity=severity,
                benign_malignant=benign_malignant,
                risk_score=round(float(effective_risk), 4),
                referral=referral,
                likely_cause=likely_cause,
                recommendation=recommendation,
                user_report=_build_user_report(
                    primary_label=primary_label,
                    severity=severity,
                    benign_malignant=benign_malignant,
                    risk_score=float(effective_risk),
                    likely_cause=likely_cause,
                    recommendation=recommendation,
                    abcde=abcde_features,
                ),
                disclaimer="Herramienta de cribado y apoyo a la decisión clínica por IA. No sustituye el diagnóstico anatomopatológico.",
                abcde_analysis=abcde_features
            )
        except Exception as e:
            print(f"Aviso en inferencia CNN ({e}), usando fallback...")

    # 2. Fallback Heuristico
    resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY).astype(np.float32)
    contrast = float(np.std(gray) / 128.0)
    risk_score = float(np.clip(contrast * 0.5, 0.0, 1.0))
    
    primary_label = "enfermo" if risk_score >= 0.35 else "sano"
    severity = "peligro" if risk_score >= 0.35 else "ninguno"
    benign_malignant = "maligno_probable" if risk_score >= 0.35 else "benigno_probable"
    referral = risk_score >= 0.35
    likely_cause = "Lesión evaluada mediante análisis de contingencia"
    recommendation = "Revisión dermatológica recomendada." if referral else "Seguimiento preventivo."

    return AnalysisResponse(
        filename=filename or "imagen_subida",
        primary_label=primary_label,
        severity=severity,
        benign_malignant=benign_malignant,
        risk_score=round(risk_score, 4),
        referral=referral,
        likely_cause=likely_cause,
        recommendation=recommendation,
        user_report=_build_user_report(
            primary_label=primary_label,
            severity=severity,
            benign_malignant=benign_malignant,
            risk_score=risk_score,
            likely_cause=likely_cause,
            recommendation=recommendation,
            abcde=abcde_features,
        ),
        disclaimer="Herramienta de cribado y apoyo a la decisión clínica por IA. No sustituye el diagnóstico anatomopatológico.",
        abcde_analysis=abcde_features
    )
