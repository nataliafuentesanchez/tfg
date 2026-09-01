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
import os
from typing import Optional
try:
    import joblib
    _JOBLIB_AVAILABLE = True
except Exception:
    _JOBLIB_AVAILABLE = False

# Optional model used as a cascaded filter to reduce false positives.
_FILTER_MODEL_PATH = os.path.join(os.getcwd(), "models", "filter_model.joblib")
_filter_model = None

# Supervised RandomForest model for better classification
_SUPERVISED_MODEL_PATH = os.path.join(os.getcwd(), "models", "supervised_model.joblib")
_supervised_model = None

# Scaler for supervised model
_SCALER_PATH = os.path.join(os.getcwd(), "models", "supervised_scaler.joblib")
_scaler = None

# Numpy-based filter model (weights and normalization)
_FILTER_NUMPY_PATH = os.path.join(os.getcwd(), "models", "filter_numpy.npz")
_numpy_filter = None


def _load_supervised_model() -> Optional[object]:
    """Carga el modelo RandomForest entrenado."""
    global _supervised_model
    if _supervised_model is not None:
        return _supervised_model
    if not _JOBLIB_AVAILABLE:
        return None
    try:
        if os.path.exists(_SUPERVISED_MODEL_PATH):
            _supervised_model = joblib.load(_SUPERVISED_MODEL_PATH)
            return _supervised_model
    except Exception:
        return None
    return None


def _load_scaler() -> Optional[object]:
    """Carga el scaler para normalizar features."""
    global _scaler
    if _scaler is not None:
        return _scaler
    if not _JOBLIB_AVAILABLE:
        return None
    try:
        if os.path.exists(_SCALER_PATH):
            _scaler = joblib.load(_SCALER_PATH)
            return _scaler
    except Exception:
        return None
    return None


def _load_numpy_filter() -> dict | None:
    global _numpy_filter
    if _numpy_filter is not None:
        return _numpy_filter
    if os.path.exists(_FILTER_NUMPY_PATH):
        try:
            import numpy as _np

            data = _np.load(_FILTER_NUMPY_PATH, allow_pickle=True)
            _numpy_filter = {
                "w": data["w"],
                "mean": data["mean"],
                "std": data["std"],
                "cols": [str(x) for x in data["cols"].tolist()],
                "cutoff": float(data["cutoff"]) if "cutoff" in data.files else 0.5,
            }
            return _numpy_filter
        except Exception:
            return None
    return None

def _load_filter_model() -> Optional[object]:
    global _filter_model
    if _filter_model is not None:
        return _filter_model
    if not _JOBLIB_AVAILABLE:
        return None
    try:
        if os.path.exists(_FILTER_MODEL_PATH):
            _filter_model = joblib.load(_FILTER_MODEL_PATH)
            return _filter_model
    except Exception:
        return None
    return None


def _load_filter_rules() -> dict | None:
    rules_path = os.path.join(os.getcwd(), "models", "filter_rules.json")
    if os.path.exists(rules_path):
        try:
            import json

            with open(rules_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None

URGENT_REFERRAL_THRESHOLD = 0.80
PRIMARY_LABEL_THRESHOLD = 0.55
MALIGNANT_THRESHOLD = 0.82
MIN_HOTSPOT_FOR_MALIGNANT = 0.05


def _decode_image(content: bytes) -> np.ndarray:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Formato de imagen no valido o archivo corrupto.")
    return image


def _compute_risk_score(image: np.ndarray) -> tuple[float, dict[str, float]]:
    resized = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY).astype(np.float32)

    red_channel = rgb[:, :, 0].astype(np.float32)
    green_channel = rgb[:, :, 1].astype(np.float32)
    blue_channel = rgb[:, :, 2].astype(np.float32)
    saturation = hsv[:, :, 1].astype(np.float32)

    background_r = float(np.median(red_channel))
    background_g = float(np.median(green_channel))
    background_b = float(np.median(blue_channel))
    color_distance = np.sqrt(
        (red_channel - background_r) ** 2
        + (green_channel - background_g) ** 2
        + (blue_channel - background_b) ** 2
    )

    lesion_mask = (
        (red_channel > np.maximum(green_channel, blue_channel) + 20)
        & (red_channel > 80)
        & (saturation > 40)
        & (color_distance > 28)
    )
    lesion_mask = lesion_mask.astype(np.uint8)
    kernel = np.ones((5, 5), dtype=np.uint8)
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_OPEN, kernel)
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_CLOSE, kernel)

    lesion_pixels = float(np.mean(lesion_mask))
    lesion_ratio = min(1.0, lesion_pixels * 6.0)

    if lesion_mask.sum() > 0:
        contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 30]
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            perimeter = cv2.arcLength(largest, True)
            irregularity = (perimeter ** 2) / (4 * np.pi * area + 1e-6)
            mask_irregularity = float(np.clip(irregularity / 6.0, 0.0, 1.0))
            diameter_proxy = min(1.0, area / (resized.shape[0] * resized.shape[1] * 0.12))
        else:
            mask_irregularity = 0.0
            diameter_proxy = 0.0
    else:
        mask_irregularity = 0.0
        diameter_proxy = 0.0

    if lesion_mask.sum() > 0:
        flipped_mask = np.fliplr(lesion_mask)
        mask_pixels = float((lesion_mask > 0).sum())
        overlap = float(np.logical_and(lesion_mask > 0, flipped_mask > 0).sum()) / max(1.0, mask_pixels)
        asymmetry = float(np.clip(1.0 - overlap, 0.0, 1.0))
        # Small, symmetric lesions commonly correspond to benign nevi and should not
        # be promoted to the active disease band despite some red pigmentation.
        if lesion_pixels < 1400 and asymmetry < 0.35 and mask_irregularity < 0.50:
            asymmetry *= 0.35
    else:
        asymmetry = 0.0

    color_variance = float(np.std(rgb[lesion_mask > 0], axis=0).mean() / 255.0) if lesion_mask.sum() > 0 else 0.0
    red_hotspot_ratio = float(np.mean((red_channel > 160) & (green_channel < 140) & (blue_channel < 140)))
    contrast = float(np.std(gray) / 128.0)
    edge_density = float(np.mean(cv2.Canny(gray.astype(np.uint8), 60, 150) > 0))

    red_mean = float(np.mean(red_channel) / 255.0)
    texture_variation = float(np.std(gray) / 128.0)
    # Laplacian variance (focus / texture measure)
    laplacian_var = float(np.var(cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)))
    # HSV statistics
    hsv_mean = float(np.mean(hsv[:, :, 2]) / 255.0)
    hsv_std = float(np.std(hsv[:, :, 2]) / 255.0)
    # Simple red histogram bins (4 bins)
    red_hist = cv2.calcHist([red_channel.astype(np.uint8)], [0], None, [4], [0, 256]).flatten()
    red_hist = (red_hist / (red_hist.sum() + 1e-9)).tolist()

    score = (
        0.30 * min(1.0, lesion_ratio)  # Reduce lesion_ratio weight
        + 0.22 * min(1.0, red_hotspot_ratio * 4.0)
        + 0.22 * min(1.0, mask_irregularity)  # Increase mask_irregularity weight
        + 0.18 * min(1.0, asymmetry)  # Increase asymmetry weight
        + 0.08 * min(1.0, color_variance * 2.5)  # Reduce color_variance weight
    )
    if (
        lesion_pixels < 0.02
        and red_hotspot_ratio < 0.08
        and asymmetry < 0.05
        and mask_irregularity < 0.2
    ):
        risk_score = 0.0
    else:
        risk_score = float(np.clip(score, 0.0, 1.0))

    # Common benign nevi (NV) tend to be red but low-contrast, smooth and
    # symmetric. They should remain in the "safe" band even when local red
    # pigmentation is present, while suspicious lesions retain a higher risk score.
    # However, DO NOT suppress if asymmetry is significant (>0.65) or
    # mask_irregularity is high (>0.65), as these indicate actual lesions.
    common_nevus_guard = (
        lesion_pixels < 0.20
        and asymmetry < 0.65  # Strict asymmetry threshold to avoid suppressing real asymmetric lesions
        and mask_irregularity < 0.65  # Strict irregularity threshold
        and edge_density < 0.02
        and contrast < 0.35
        and red_mean > 0.55
        and red_hotspot_ratio < 0.72
        and color_variance < 0.18
    )
    if common_nevus_guard:
        risk_score = min(risk_score, 0.55)

    features = {
        "red_mean": red_mean,
        "contrast": contrast,
        "hotspot_ratio": red_hotspot_ratio,
        "edge_density": edge_density,
        "asymmetry": asymmetry,
        "color_variance": color_variance,
        "diameter_proxy": diameter_proxy,
        "mask_irregularity": mask_irregularity,
        "texture_variation": texture_variation,
        "laplacian_var": laplacian_var,
        "hsv_mean": hsv_mean,
        "hsv_std": hsv_std,
        "red_hist_0": red_hist[0],
        "red_hist_1": red_hist[1],
        "red_hist_2": red_hist[2],
        "red_hist_3": red_hist[3],
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
    if features["asymmetry"] > 0.18:
        return "asimetria marcada con forma no uniforme"
    if features["edge_density"] > 0.22:
        return "bordes irregulares detectados"
    if features["color_variance"] > 0.30 or features["hotspot_ratio"] > 0.18:
        return "heterogeneidad cromatica sugerente"
    if features["diameter_proxy"] > 0.55:
        return "zona lesionada grande y con mayor superficie de alarma"
    if features["contrast"] > 0.65:
        return "contraste y textura con variabilidad relevante"
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

    primary_label = "enfermo" if risk_score >= PRIMARY_LABEL_THRESHOLD else "sano"
    severity = _severity_from_score(risk_score)

    broad_symmetric_red_patch = (
        features.get("diameter_proxy", 0.0) > 0.75
        and features.get("asymmetry", 0.0) < 0.08
        and features.get("mask_irregularity", 0.0) < 0.24
        and features.get("edge_density", 0.0) < 0.03
        and features.get("contrast", 0.0) < 0.25
        and features.get("hotspot_ratio", 0.0) < 0.35
        and features.get("color_variance", 0.0) < 0.15
        and features.get("red_mean", 0.0) > 0.52
        and features.get("red_hist_1", 0.0) > 0.50
        and features.get("red_hist_3", 0.0) < 0.18
    )
    
    # Large homogeneous red patches (erythema, vascular lesions) without real
    # morphologic irregularity or asymmetry. These are typically benign despite
    # large size and redness.
    large_homogeneous_red_patch = (
        features.get("diameter_proxy", 0.0) > 0.82
        and features.get("red_mean", 0.0) > 0.73
        and features.get("color_variance", 0.0) < 0.125
        and features.get("edge_density", 0.0) < 0.035
        and features.get("mask_irregularity", 0.0) < 0.55
        and features.get("asymmetry", 0.0) < 0.55
        and features.get("contrast", 0.0) < 0.25
    )
    
    common_nevus_like = (
        features.get("red_mean", 0.0) > 0.70
        and features.get("red_hist_3", 0.0) > 0.70
        and features.get("diameter_proxy", 0.0) > 0.35
        and features.get("asymmetry", 0.0) < 0.45
        and features.get("hotspot_ratio", 0.0) < 0.75
        and features.get("color_variance", 0.0) < 0.16
        and features.get("edge_density", 0.0) < 0.02
    )
    if (broad_symmetric_red_patch or large_homogeneous_red_patch or common_nevus_like) and primary_label == "enfermo":
        risk_score = 0.45
        primary_label = "sano"
        severity = _severity_from_score(risk_score)
        benign_malignant = "benigno_probable"
        referral = False
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

    if primary_label == "sano":
        benign_malignant = "benigno_probable"
    else:
        # Require a slightly higher threshold for malignancy and a minimal hotspot
        # to reduce false positives driven by tiny noisy regions.
        if risk_score >= MALIGNANT_THRESHOLD and features.get("hotspot_ratio", 0.0) >= MIN_HOTSPOT_FOR_MALIGNANT:
            benign_malignant = "maligno_probable"
        else:
            benign_malignant = "benigno_probable"

    # Referral requires strong evidence: either very high score, or malignancy
    # combined with a minimal size proxy to avoid referring tiny false positives.
    referral = False
    if risk_score >= URGENT_REFERRAL_THRESHOLD:
        referral = True
    elif benign_malignant == "maligno_probable" and features.get("diameter_proxy", 0.0) >= 0.02:
        referral = True

    if referral:
        recommendation = (
            "Derivacion prioritaria al dermatologo recomendada para revision clinica."
        )
    elif primary_label == "enfermo":
        recommendation = "Se recomienda revision dermatologica programada."
    else:
        recommendation = "No se detecta alarma alta; mantener seguimiento preventivo."

    likely_cause = _likely_cause(features)

    # Apply cascaded filter model if available: if the model predicts SANO with
    # reasonable probability, suppress a positive result to reduce false positives.
    filter_model = _load_filter_model()
    # Try numpy filter first (preferred lightweight classifier)
    numpy_filter = _load_numpy_filter()
    if numpy_filter is not None:
        try:
            import numpy as _np

            feat_cols = numpy_filter["cols"]
            feat_vec = _np.array([features.get(c, 0.0) for c in feat_cols], dtype=float)
            mean = numpy_filter["mean"]
            std = numpy_filter["std"]
            w = numpy_filter["w"]
            feat_n = (feat_vec - mean) / (std + 1e-9)
            xb = _np.concatenate([_np.array([1.0]), feat_n])
            logit = float(xb.dot(w))
            prob = 1.0 / (1.0 + _np.exp(-max(-50.0, min(50.0, logit))))
            # use cutoff saved in model (default 0.5)
            cutoff = float(numpy_filter.get("cutoff", 0.5))
            if prob >= cutoff:
                # predicts SANO -> suppress positive
                if primary_label == "enfermo":
                    risk_score = 0.0
                    primary_label = "sano"
                    severity = _severity_from_score(risk_score)
                    benign_malignant = "benigno_probable"
                    referral = False
                    recommendation = "No se detecta alarma alta; mantener seguimiento preventivo."
                    likely_cause = _likely_cause(features)
        except Exception:
            pass
    if filter_model is not None:
        try:
            feat_vec = [
                features.get("red_mean", 0.0),
                features.get("hotspot_ratio", 0.0),
                features.get("diameter_proxy", 0.0),
                features.get("asymmetry", 0.0),
                features.get("color_variance", 0.0),
                features.get("edge_density", 0.0),
                features.get("texture_variation", 0.0),
                features.get("laplacian_var", 0.0),
                features.get("hsv_mean", 0.0),
                features.get("hsv_std", 0.0),
                features.get("red_hist_0", 0.0),
                features.get("red_hist_1", 0.0),
                features.get("red_hist_2", 0.0),
                features.get("red_hist_3", 0.0),
            ]
            prob = filter_model.predict_proba([feat_vec])
            # prob[0][0] = probability of class 0 (SANO)
            if prob[0][0] >= 0.7:
                # Strong evidence of SANO: reduce risk significantly
                risk_score = 0.0
                primary_label = "sano"
                severity = _severity_from_score(risk_score)
                benign_malignant = "benigno_probable"
                referral = False
                recommendation = "No se detecta alarma alta; mantener seguimiento preventivo."
                likely_cause = _likely_cause(features)
        except Exception:
            pass
    else:
        # Try rule-based filter if model not available
        rules = _load_filter_rules()
        if rules:
            try:
                # If predicted positive but fails minimal feature thresholds, suppress
                if primary_label == "enfermo":
                    suppress = False
                    # diameter
                    if features.get("diameter_proxy", 0.0) < rules.get("diameter_proxy_min", 0.0):
                        suppress = True
                    if features.get("hotspot_ratio", 0.0) < rules.get("hotspot_ratio_min", 0.0):
                        suppress = True
                    if features.get("color_variance", 0.0) < rules.get("color_variance_min", 0.0):
                        suppress = True
                    if features.get("laplacian_var", 0.0) < rules.get("laplacian_var_min", 0.0):
                        suppress = True
                    if suppress:
                        risk_score = 0.0
                        primary_label = "sano"
                        severity = _severity_from_score(risk_score)
                        benign_malignant = "benigno_probable"
                        referral = False
                        recommendation = "No se detecta alarma alta; mantener seguimiento preventivo."
                        likely_cause = _likely_cause(features)
            except Exception:
                pass

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
