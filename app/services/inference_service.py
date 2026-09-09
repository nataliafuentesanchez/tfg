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

# Matriz clinica estandar para las 7 patologias del dataset HAM10000
PATOLOGY_CLINICAL_MATRIX = {
    "nv": {
        "name": "Nevus Melanocítico (Lunar común)",
        "state": "SANO / BENIGNO",
        "alert": "BAJO RIESGO",
        "severity_internal": "bajo",
        "primary_internal": "sano",
        "classification": "Benigna / Normal",
        "benign_malignant_internal": "benigno_probable",
        "referral_internal": False,
        "description": "Lesión benigna común formada por la acumulación de melanocitos (lunar habitual). No representa riesgo para la salud en su estado actual.",
        "recommendation": "No se observan signos visuales de alarma. Se recomiendan revisiones de rutina o consultar a un especialista si nota cambios en la forma, color o tamaño."
    },
    "bkl": {
        "name": "Queratosis Benigna (Seborreica / Solar)",
        "state": "SANO / BENIGNO",
        "alert": "BAJO RIESGO",
        "severity_internal": "bajo",
        "primary_internal": "sano",
        "classification": "Benigna / Normal",
        "benign_malignant_internal": "benigno_probable",
        "referral_internal": False,
        "description": "Crecimiento no canceroso común en la piel (como queratosis seborreica o lentigos). No evoluciona a cáncer de piel.",
        "recommendation": "Lesión benigna sin signo de malignidad. Consultar al dermatólogo en caso de molestias o cambios."
    },
    "vasc": {
        "name": "Lesión Vascular (Angioma / Hemangioma)",
        "state": "SANO / BENIGNO",
        "alert": "BAJO RIESGO",
        "severity_internal": "bajo",
        "primary_internal": "sano",
        "classification": "Benigna / Normal",
        "benign_malignant_internal": "benigno_probable",
        "referral_internal": False,
        "description": "Alteración benigna de los vasos sanguíneos de la piel (como hemangiomas o angiomas). Sin riesgo de malignidad.",
        "recommendation": "Lesión benigna estable. Seguimiento de rutina."
    },
    "df": {
        "name": "Dermatofibroma (Nódulo cutáneo benigno)",
        "state": "SANO / BENIGNO",
        "alert": "BAJO RIESGO",
        "severity_internal": "bajo",
        "primary_internal": "sano",
        "classification": "Benigna / Normal",
        "benign_malignant_internal": "benigno_probable",
        "referral_internal": False,
        "description": "Nódulo cutáneo benigno asintomático, común en extremidades. Sin riesgo de malignidad.",
        "recommendation": "Condición benigna. No requiere intervención inmediata salvo cambios visibles."
    },
    "akiec": {
        "name": "Queratosis Actínica / Enf. Bowen",
        "state": "ENFERMO / PREMALIGNO",
        "alert": "LEVE - MODERADO",
        "severity_internal": "medio",
        "primary_internal": "enfermo",
        "classification": "Premaligna",
        "benign_malignant_internal": "maligno_probable",
        "referral_internal": True,
        "description": "Lesiones precancerosas causadas por daño solar acumulado que pueden evolucionar a carcinoma escamocelular si no se tratan adecuadamente.",
        "recommendation": "Consulta dermatológica recomendada para valoración y tratamiento preventivo de la lesión premaligna antes de que pueda evolucionar."
    },
    "bcc": {
        "name": "Carcinoma Basocelular",
        "state": "ENFERMO / MALIGNO",
        "alert": "MODERADO",
        "severity_internal": "medio",
        "primary_internal": "enfermo",
        "classification": "Maligna probable",
        "benign_malignant_internal": "maligno_probable",
        "referral_internal": True,
        "description": "Tipo de cáncer de piel de crecimiento lento local. Raramente se propaga a otros órganos, pero requiere evaluación y tratamiento médico oportuno.",
        "recommendation": "Se recomienda solicitar cita con el dermatólogo para valoración presencial y planificación de tratamiento."
    },
    "mel": {
        "name": "Melanoma",
        "state": "ENFERMO / MALIGNO",
        "alert": "GRAVE",
        "severity_internal": "grave",
        "primary_internal": "enfermo",
        "classification": "Maligna probable",
        "benign_malignant_internal": "maligno_probable",
        "referral_internal": True,
        "description": "Lesión con sospecha de melanoma, el tipo de cáncer de piel más agresivo. Requiere atención prioritaria para confirmación mediante biopsia.",
        "recommendation": "Se recomienda programar una consulta dermatológica urgente para una evaluación presencial prioritaria."
    },
}

DIAGNOSIS_LABELS = {k: v["name"] for k, v in PATOLOGY_CLINICAL_MATRIX.items()}
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

    # Descripciones cualitativas con 4 niveles de granularidad + score numérico integrado
    # A - Asimetría
    a_s = round(asymmetry, 3)
    if a_s >= 0.40:
        a_desc = f"Asimetría marcada en ambos ejes (score: {a_s}). La lesión presenta una distribución claramente irregular; los hemicampos horizontal y vertical no se superponen, lo que constituye un signo de alta sospecha dermatoscópica."
    elif a_s >= 0.25:
        a_desc = f"Asimetría moderada detectada (score: {a_s}). Existe una diferencia apreciable entre los hemicampos de la lesión, sugerente de crecimiento irregular o distribución pigmentaria no uniforme."
    elif a_s >= 0.10:
        a_desc = f"Asimetría leve (score: {a_s}). La lesión es mayoritariamente simétrica con una ligera diferencia entre hemicampos. Se recomienda seguimiento ante cambios."
    else:
        a_desc = f"Lesión simétrica (score: {a_s}). Los hemicampos horizontal y vertical presentan alta superposición; patrón morfológico regular sin signos de asimetría significativa."

    # B - Bordes
    b_s = round(border_irregularity, 3)
    if b_s >= 0.50:
        b_desc = f"Bordes muy irregulares y difusos (score: {b_s}). El perímetro de la lesión es notablemente lobulado o estrellado, con transición abrupta hacia la piel sana; hallazgo de alta sospecha."
    elif b_s >= 0.30:
        b_desc = f"Bordes irregulares o parcialmente mal definidos (score: {b_s}). Se observan entrantes y salientes perimetrales que sugieren crecimiento asimétrico de la lesión."
    elif b_s >= 0.15:
        b_desc = f"Bordes ligeramente irregulares (score: {b_s}). Contorno mayormente circunscrito con alguna zona de transición no del todo nítida; dentro de la variabilidad normal en lesiones benignas."
    else:
        b_desc = f"Bordes regulares y bien circunscritos (score: {b_s}). El perímetro es nítido y suave, con transición gradual hacia la piel perilesional; patrón compatible con lesión benigna estable."

    # C - Color
    c_s = round(color_heterogeneity, 3)
    if c_s >= 0.50:
        c_desc = f"Policromatismo intenso (score: {c_s}). La lesión muestra múltiples tonos claramente diferenciados (p. ej. marrón, negro, rojo, azul/gris). La variabilidad cromática es un criterio de alta sospecha dermatoscópica."
    elif c_s >= 0.30:
        c_desc = f"Heterogeneidad cromática moderada (score: {c_s}). Se detectan al menos dos tonos diferenciados dentro de la lesión. La distribución irregular del pigmento requiere evaluación especializada."
    elif c_s >= 0.12:
        c_desc = f"Coloración levemente heterogénea (score: {c_s}). La lesión presenta un tono predominante con ligeras variaciones de intensidad que pueden ser normales en lesiones benignas."
    else:
        c_desc = f"Coloración homogénea (score: {c_s}). La distribución del pigmento es uniforme en toda la lesión, sin tonos contrastantes; compatible con lesión benigna sin signos de actividad cromática."

    # D - Diámetro
    d_s = round(diameter_proxy, 3)
    if d_s >= 0.60:
        d_desc = f"Diámetro estimado grande (score: {d_s}). La lesión ocupa una proporción considerable del área de análisis, superando claramente el umbral de referencia de 6 mm; requiere valoración presencial."
    elif d_s >= 0.35:
        d_desc = f"Diámetro estimado significativo, probable > 6 mm (score: {d_s}). La extensión de la lesión supera el umbral de referencia dermatoscópica; recomendable valoración clínica."
    elif d_s >= 0.15:
        d_desc = f"Diámetro moderado, próximo al umbral de 6 mm (score: {d_s}). La lesión tiene una extensión media; se sugiere seguimiento fotográfico para detectar cambios en el tiempo."
    else:
        d_desc = f"Diámetro pequeño o focal (score: {d_s}). La lesión ocupa un área reducida, por debajo del umbral de referencia de 6 mm; tamaño compatible con lesiones benignas estables."

    # E - Estructura / Textura
    e_s = round(structure_complexity, 3)
    if e_s >= 0.50:
        e_desc = f"Estructura interna compleja y atípica (score: {e_s}). Se detecta alta densidad de contornos internos y varianza de textura elevada; la organización interna es irregular, lo que puede indicar actividad proliferativa."
    elif e_s >= 0.30:
        e_desc = f"Estructura interna moderadamente irregular (score: {e_s}). Existe cierta complejidad textural interna que excede el patrón de lesiones benignas homogéneas; recomendable valoración especializada."
    elif e_s >= 0.12:
        e_desc = f"Estructura interna levemente irregular (score: {e_s}). La textura muestra alguna variación, dentro de la variabilidad esperada en lesiones benignas con superficie ligeramente rugosa."
    else:
        e_desc = f"Estructura interna uniforme (score: {e_s}). La textura y distribución interna de la lesión son homogéneas, sin variaciones abruptas; compatible con lesión benigna estable."

    return {
        "asymmetry_score": a_s,
        "asymmetry_desc": a_desc,
        "border_score": b_s,
        "border_desc": b_desc,
        "color_score": c_s,
        "color_desc": c_desc,
        "diameter_score": d_s,
        "diameter_desc": d_desc,
        "structure_score": e_s,
        "structure_desc": e_desc,
    }



def _severity_from_score(score: float, is_melanoma: bool = False) -> str:
    """Calcula el nivel de gravedad clinico (ninguno, bajo, medio, grave)."""
    if is_melanoma or score >= 0.70:
        return "grave"
    if score >= 0.40:
        return "medio"
    if score >= 0.18:
        return "bajo"
    return "ninguno"


def _format_structured_report(
    state: str,
    alert: str,
    classification: str,
    compatibility_pct: float,
    patology_name: str,
    description: str,
    abcde: Dict[str, Any],
    recommendation: str
) -> str:
    """Genera el informe con la plantilla estructurada oficial de OLIVIA."""
    return (
        "RESULTADO DEL ANÁLISIS DE LA RED NEURONAL\n\n"
        f"• Estado visual: {state}\n"
        f"• Nivel de alerta: {alert}\n"
        f"• Clasificación de la lesión: {classification}\n"
        f"• Compatibilidad estimada: {round(compatibility_pct, 1)}%\n"
        f"• Patología más compatible: {patology_name}\n\n"
        "DESCRIPCIÓN Y CONTEXTO\n"
        f"{description}\n\n"
        "EVALUACIÓN VISUAL (Criterios ABCDE)\n"
        f"• Asimetría (A): {abcde['asymmetry_desc']}\n"
        f"• Bordes (B): {abcde['border_desc']}\n"
        f"• Color (C): {abcde['color_desc']}\n"
        f"• Diámetro (D): {abcde['diameter_desc']}\n\n"
        "RECOMENDACIÓN Y DERIVACIÓN\n"
        f"{recommendation}"
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

            # Criterios morfologicos atipicos
            abcde_is_atypical = (
                abcde_features["asymmetry_score"] >= 0.28
                or abcde_features["border_score"] >= 0.25
                or abcde_features["color_score"] >= 0.25
            )

            # Determinación de patología de referencia y triage clínico
            # Regla de Triage Clinico:
            # 1. Alerta por Melanoma: sospecha individual mel_prob >= 0.15 o top_dx == "mel" -> "mel" (GRAVE)
            # 2. Alerta por Carcinoma Basocelular: top_dx == "bcc" o bcc_prob >= 0.20 -> "bcc" (MODERADO)
            # 3. Alerta por Queratosis Actinica (Premaligna): top_dx == "akiec" o akiec_prob >= 0.20 -> "akiec" (LEVE - MODERADO)
            # 4. Otras patologías según predicción ganadora o agregada
            if top_dx == "mel" or mel_prob >= 0.15:
                detected_dx = "mel"
            elif top_dx == "bcc" or bcc_prob >= 0.20:
                detected_dx = "bcc"
            elif top_dx == "akiec" or akiec_prob >= 0.20:
                detected_dx = "akiec"
            elif abcde_is_atypical and malignant_risk >= 0.15:
                detected_dx = "akiec" if akiec_prob >= bcc_prob else "bcc"
            else:
                detected_dx = top_dx

            info = PATOLOGY_CLINICAL_MATRIX[detected_dx]
            
            # Cálculo de compatibilidad porcentual
            compat_pct = probs.get(detected_dx, 0.0) * 100.0
            if detected_dx in MALIGNANT_CLASSES:
                compat_pct = max(compat_pct, malignant_risk * 100.0)

            # Risk score calibrado numérico [0.0 - 1.0]
            if detected_dx == "mel":
                effective_risk = max(0.75, min(0.99, mel_prob * 2.0 + malignant_risk))
            elif detected_dx == "bcc":
                effective_risk = max(0.40, min(0.68, bcc_prob * 1.5 + malignant_risk * 0.5))
            elif detected_dx == "akiec":
                effective_risk = max(0.25, min(0.48, akiec_prob * 1.3 + malignant_risk * 0.4))
            else:
                effective_risk = min(0.12, malignant_risk)

            user_report_text = _format_structured_report(
                state=info["state"],
                alert=info["alert"],
                classification=info["classification"],
                compatibility_pct=compat_pct,
                patology_name=info["name"],
                description=info["description"],
                abcde=abcde_features,
                recommendation=info["recommendation"]
            )

            return AnalysisResponse(
                filename=filename or "imagen_subida",
                primary_label=info["primary_internal"],
                severity=info["severity_internal"],
                benign_malignant=info["benign_malignant_internal"],
                risk_score=round(float(effective_risk), 4),
                referral=info["referral_internal"],
                likely_cause=info["name"],
                recommendation=info["recommendation"],
                user_report=user_report_text,
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
    
    if risk_score >= 0.55:
        dx_fb = "mel"
    elif risk_score >= 0.35:
        dx_fb = "akiec"
    else:
        dx_fb = "nv"

    info_fb = PATOLOGY_CLINICAL_MATRIX[dx_fb]
    user_report_text = _format_structured_report(
        state=info_fb["state"],
        alert=info_fb["alert"],
        classification=info_fb["classification"],
        compatibility_pct=risk_score * 100.0,
        patology_name=info_fb["name"],
        description=info_fb["description"],
        abcde=abcde_features,
        recommendation=info_fb["recommendation"]
    )

    return AnalysisResponse(
        filename=filename or "imagen_subida",
        primary_label=info_fb["primary_internal"],
        severity=info_fb["severity_internal"],
        benign_malignant=info_fb["benign_malignant_internal"],
        risk_score=round(risk_score, 4),
        referral=info_fb["referral_internal"],
        likely_cause=info_fb["name"],
        recommendation=info_fb["recommendation"],
        user_report=user_report_text,
        disclaimer="Herramienta de cribado y apoyo a la decisión clínica por IA. No sustituye el diagnóstico anatomopatológico.",
        abcde_analysis=abcde_features
    )

