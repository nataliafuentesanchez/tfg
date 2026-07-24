# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import cv2
import numpy as np

from app.services.inference_service import (
    URGENT_REFERRAL_THRESHOLD,
    _severity_from_score,
    analyze_image,
)


def test_severity_mapping() -> None:
    assert _severity_from_score(0.10) == "ninguno"
    assert _severity_from_score(0.55) == "bajo"
    assert _severity_from_score(0.70) == "medio"
    assert _severity_from_score(0.95) == "peligro"


def test_urgent_threshold_is_conservative() -> None:
    assert URGENT_REFERRAL_THRESHOLD == 0.80


def test_analysis_includes_user_report() -> None:
    image = np.full((64, 64, 3), 180, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="demo.jpg")
    assert result.user_report
    assert "Resultado principal" in result.user_report
