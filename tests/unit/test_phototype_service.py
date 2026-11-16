# =============================================================================
# AnalisisImagenes — Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import cv2
import numpy as np
import pytest
from app.services.phototype_service import PhototypeService


def test_phototype_fallback_on_invalid_image() -> None:
    res_none = PhototypeService.estimate_phototype(None)  # type: ignore
    assert res_none.fitzpatrick_scale == "III"

    empty_img = np.zeros((0, 0, 3), dtype=np.uint8)
    res_empty = PhototypeService.estimate_phototype(empty_img)
    assert res_empty.fitzpatrick_scale == "III"

    tiny_img = np.zeros((5, 5, 3), dtype=np.uint8)
    res_tiny = PhototypeService.estimate_phototype(tiny_img)
    assert res_tiny.fitzpatrick_scale == "III"


def test_phototype_very_fair_skin_fototipo_i_or_ii() -> None:
    # Piel muy clara / blanca nórdica (R alto, G medio-alto, B medio-alto)
    # BGR en OpenCV: B=195, G=215, R=245
    fair_skin = np.full((120, 120, 3), (195, 215, 245), dtype=np.uint8)
    res = PhototypeService.estimate_phototype(fair_skin)
    assert res.fitzpatrick_scale in ["I", "II"]
    assert res.ita_angle > 41.0
    assert "FPS 50+" in res.recommended_spf


def test_phototype_intermediate_mediterranean_fototipo_iii_or_iv() -> None:
    # Piel intermedia / mediterránea clara a morena
    # BGR en OpenCV: B=120, G=160, R=210
    med_skin = np.full((120, 120, 3), (120, 160, 210), dtype=np.uint8)
    res = PhototypeService.estimate_phototype(med_skin)
    assert res.fitzpatrick_scale in ["III", "IV"]
    assert "FPS 30" in res.recommended_spf


def test_phototype_dark_skin_fototipo_v_or_vi() -> None:
    # Piel muy pigmentada / oscura
    # BGR en OpenCV: B=40, G=55, R=75
    dark_skin = np.full((120, 120, 3), (40, 55, 75), dtype=np.uint8)
    res = PhototypeService.estimate_phototype(dark_skin)
    assert res.fitzpatrick_scale in ["V", "VI"]
    assert res.ita_angle < 10.0


def test_phototype_with_lesion_mask() -> None:
    # Imagen con lesión oscura en el centro y piel clara en la periferia
    img = np.full((100, 100, 3), (170, 200, 235), dtype=np.uint8)
    # Lesión en el centro (círculo oscuro)
    cv2.circle(img, (50, 50), 20, (30, 40, 60), -1)

    # Máscara donde 255 es la lesión
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (50, 50), 20, 255, -1)

    res = PhototypeService.estimate_phototype(img, lesion_mask=mask)
    # Debe evaluar la piel perilesional (clara), no el círculo oscuro
    assert res.fitzpatrick_scale in ["I", "II", "III"]
    assert res.ita_angle > 28.0

