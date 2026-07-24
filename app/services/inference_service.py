# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

import cv2
import numpy as np

from app.schemas.prediction import AnalysisResponse

URGENT_REFERRAL_THRESHOLD = 0.80


def _decode_image(content: bytes) -> np.ndarray:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Formato de imagen no valido o archivo corrupto.")
    return image


def _compute_risk_score(image: np.ndarray) -> tuple[float, dict[str, float]]:
    resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    red_channel = rgb[:, :, 0].astype(np.float32)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY).astype(np.float32)

    red_mean = float(np.mean(red_channel) / 255.0)
    contrast = float(np.std(gray) / 128.0)
    hotspot_ratio = float(np.mean(red_channel > 200))
    edge_density = float(np.mean(cv2.Canny(gray.astype(np.uint8), 80, 150) > 0))

    score = (
        0.34 * min(1.0, red_mean)
        + 0.28 * min(1.0, contrast)
        + 0.26 * min(1.0, hotspot_ratio * 3.0)
        + 0.12 * min(1.0, edge_density * 4.0)
    )
    risk_score = float(np.clip(score, 0.0, 1.0))

    features = {
        "red_mean": red_mean,
        "contrast": contrast,
        "hotspot_ratio": hotspot_ratio,
        "edge_density": edge_density,
    }
    return risk_score, features


def _severity_from_score(score: float) -> str:
    if score < 0.50:
        return "ninguno"
    if score < 0.65:
        return "bajo"
    if score < 0.80:
        return "medio"
    return "peligro"


def _likely_cause(features: dict[str, float]) -> str:
    if features["hotspot_ratio"] > 0.22:
        return "patron inflamatorio o vascular elevado"
    if features["contrast"] > 0.65:
        return "heterogeneidad pigmentaria marcada"
    if features["edge_density"] > 0.22:
        return "bordes irregulares detectados"
    return "patron visual sin hallazgos de alta alarma"


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
) -> str:
    risk_percent = round(risk_score * 100, 1)
    return (
        f"Resultado principal: {_human_primary_label(primary_label)}. "
        f"Nivel de gravedad estimado: {severity}. "
        f"Clasificacion de lesion: {_human_benign_malignant(benign_malignant)}. "
        f"Riesgo estimado: {risk_percent}%. "
        f"Posible causa visual: {likely_cause}. "
        f"Recomendacion: {recommendation}"
    )


def analyze_image(content: bytes, filename: str | None = None) -> AnalysisResponse:
    image = _decode_image(content)
    risk_score, features = _compute_risk_score(image)

    primary_label = "enfermo" if risk_score >= 0.50 else "sano"
    severity = _severity_from_score(risk_score)

    if primary_label == "sano":
        benign_malignant = "benigno_probable"
    else:
        benign_malignant = "maligno_probable" if risk_score >= 0.75 else "benigno_probable"

    referral = bool(risk_score >= URGENT_REFERRAL_THRESHOLD or benign_malignant == "maligno_probable")

    if referral:
        recommendation = (
            "Derivacion prioritaria al dermatologo recomendada para revision clinica."
        )
    elif primary_label == "enfermo":
        recommendation = "Se recomienda revision dermatologica programada."
    else:
        recommendation = "No se detecta alarma alta; mantener seguimiento preventivo."

    likely_cause = _likely_cause(features)

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
        ),
        disclaimer="Resultado orientativo de apoyo. No equivale a diagnostico medico.",
    )
