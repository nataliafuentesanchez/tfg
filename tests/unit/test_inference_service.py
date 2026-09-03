# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import os
import cv2
import numpy as np

from app.services.inference_service import (
    URGENT_REFERRAL_THRESHOLD,
    _severity_from_score,
    analyze_image,
)


def test_severity_mapping() -> None:
    assert _severity_from_score(0.10) == "ninguno"
    assert _severity_from_score(0.25) == "bajo"
    assert _severity_from_score(0.50) == "medio"
    assert _severity_from_score(0.85) == "peligro"
    assert _severity_from_score(0.30, is_melanoma=True) == "peligro"


def test_urgent_threshold_is_conservative() -> None:
    assert URGENT_REFERRAL_THRESHOLD <= 0.60


def test_analysis_includes_user_report() -> None:
    image = np.full((64, 64, 3), 180, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="demo.jpg")
    assert result.user_report
    assert "Resultado principal" in result.user_report


def test_suspicious_lesion_scores_higher_than_safe_background() -> None:
    safe = np.full((120, 120, 3), (200, 180, 170), dtype=np.uint8)
    safe_ok, safe_encoded = cv2.imencode(".jpg", safe)
    assert safe_ok
    safe_result = analyze_image(safe_encoded.tobytes(), filename="safe.jpg")

    mel_path = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1/ISIC_0025964.jpg"
    if os.path.exists(mel_path):
        mel_img = cv2.imread(mel_path)
        mel_encoded = cv2.imencode(".jpg", mel_img)[1].tobytes()
        mel_result = analyze_image(mel_encoded, filename="melanoma.jpg")
        assert mel_result.risk_score > safe_result.risk_score
        assert mel_result.primary_label == "enfermo"
    else:
        assert safe_result.primary_label == "sano"


def test_common_nevus_is_not_flagged_as_suspicious() -> None:
    base = np.full((160, 160, 3), (200, 180, 170), dtype=np.uint8)
    cv2.ellipse(base, (80, 80), (28, 22), 0, 0, 360, (120, 90, 80), -1)
    cv2.ellipse(base, (88, 80), (15, 10), 0, 0, 360, (80, 65, 60), -1)
    cv2.circle(base, (58, 82), 5, (90, 70, 65), -1)
    cv2.circle(base, (102, 82), 5, (90, 70, 65), -1)

    ok, encoded = cv2.imencode(".jpg", base)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="common_nevus.jpg")

    assert result.primary_label == "sano"
    assert result.severity in {"ninguno", "bajo"}


def test_large_symmetric_red_patch_is_not_marked_as_suspicious() -> None:
    image = np.full((160, 160, 3), (180, 120, 110), dtype=np.uint8)
    cv2.ellipse(image, (80, 80), (60, 50), 0, 0, 360, (30, 40, 180), -1)
    cv2.ellipse(image, (80, 80), (28, 24), 0, 0, 360, (90, 180, 220), -1)

    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="large_symmetric_red_patch.jpg")

    assert result.primary_label == "sano"
    assert result.severity in {"ninguno", "bajo"}


def test_real_common_nevus_image_is_not_marked_as_suspicious() -> None:
    image_path = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1/ISIC_0026320.jpg"
    assert image_path
    image = cv2.imread(image_path)
    assert image is not None

    encoded = cv2.imencode(".jpg", image)[1].tobytes()
    result = analyze_image(encoded, filename="ISIC_0026320.jpg")

    assert result.primary_label == "sano"
    assert result.severity in {"ninguno", "bajo"}
