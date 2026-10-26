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
    assert _severity_from_score(0.85) == "grave"
    assert _severity_from_score(0.30, is_melanoma=True) == "grave"


def test_urgent_threshold_is_conservative() -> None:
    assert URGENT_REFERRAL_THRESHOLD <= 0.60


def test_analysis_includes_user_report() -> None:
    image = np.full((64, 64, 3), 180, dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="demo.jpg")
    assert result.user_report
    assert result.image_base64 is not None
    assert result.image_base64.startswith("data:image/jpeg;base64,")
    assert "RESULTADO DEL ANÁLISIS DE LA RED NEURONAL" in result.user_report
    assert "EVALUACIÓN VISUAL (Criterios ABCDE)" in result.user_report
    assert "RECOMENDACIÓN Y DERIVACIÓN" in result.user_report


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
        assert mel_result.severity in {"medio", "grave"}
    else:
        assert safe_result.primary_label == "sano"
        assert safe_result.severity in {"ninguno", "bajo"}



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


def test_large_symmetric_benign_patch_is_not_marked_as_suspicious() -> None:
    """
    Test con imagen sintetica de nevus benigno: fondo piel clara y lesion marron centrada
    con forma simetrica y colores uniformes - patron tipico de lunar benigno.
    Los colores azul/cian anteriores eran clinicamente ambiguos (similares a lesiones vasculares).
    """
    # Fondo: tono piel rosado claro
    image = np.full((160, 160, 3), (205, 175, 160), dtype=np.uint8)
    # Lesion central: marron uniforme (nevus benigno tipico)
    cv2.ellipse(image, (80, 80), (55, 48), 0, 0, 360, (105, 75, 60), -1)
    # Interior ligeramente mas oscuro pero mismo tono cafe
    cv2.ellipse(image, (80, 80), (30, 26), 0, 0, 360, (85, 58, 44), -1)

    ok, encoded = cv2.imencode(".jpg", image)
    assert ok

    result = analyze_image(encoded.tobytes(), filename="large_symmetric_benign_patch.jpg")

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


def test_clinical_calibration_user_reported_cases() -> None:
    """Verifica que los casos reportados por la usuaria se clasifiquen con su patología clínica real."""
    base_ham = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1"
    base_user = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/pruebas_imagenes_olivia"

    # Nevus comunes de la base de datos (deben ser sanos / nv)
    for nv_file in ["ISIC_0025412.jpg", "ISIC_0024317.jpg"]:
        p = os.path.join(base_ham, nv_file)
        if os.path.exists(p):
            with open(p, "rb") as f:
                res = analyze_image(f.read(), filename=nv_file)
            assert res.primary_label == "sano"
            assert "Nevus" in res.likely_cause

    # Melanoma real de prueba (debe ser maligno / mel / grave)
    mel_file = os.path.join(base_user, "433595.jpeg")
    if os.path.exists(mel_file):
        with open(mel_file, "rb") as f:
            res_mel = analyze_image(f.read(), filename="433595.jpeg")
        assert res_mel.primary_label == "enfermo"
        assert res_mel.severity == "grave"
        assert "Melanoma" in res_mel.likely_cause

    # Queratosis actínica (deben ser premalignas / akiec)
    for q_file in ["gr1.jpeg", "images45.jpeg"]:
        p = os.path.join(base_user, q_file)
        if os.path.exists(p):
            with open(p, "rb") as f:
                res_q = analyze_image(f.read(), filename=q_file)
            assert res_q.primary_label == "enfermo"
            assert "Queratosis Actínica" in res_q.likely_cause


def test_clinical_calibration_melanoma_vs_carcinoma_conflict_resolution() -> None:
    """Verifica la resolución de conflictos clínicos entre Melanoma (ISIC_0032258), Carcinomas y Queratosis Actínicas."""
    base_ham1 = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_1"
    base_ham2 = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/imagenes/HAM10000_images_part_2"
    base_user = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/pruebas_imagenes_olivia"

    # 1. Melanoma real biopsiado reportado por la usuaria que se confundía con Carcinoma (ISIC_0032258)
    p_mel = os.path.join(base_ham2, "ISIC_0032258.jpg")
    if os.path.exists(p_mel):
        with open(p_mel, "rb") as f:
            res_mel = analyze_image(f.read(), filename="ISIC_0032258.jpg")
        assert res_mel.primary_label == "enfermo"
        assert res_mel.severity == "grave"
        assert "Melanoma" in res_mel.likely_cause

    # 2. Carcinomas basocelulares reales que se sobreescribían falsamente a Queratosis Actínica
    # Caso HAM10000 (ISIC_0029392)
    p_bcc_ham = os.path.join(base_ham2, "ISIC_0029392.jpg")
    if os.path.exists(p_bcc_ham):
        with open(p_bcc_ham, "rb") as f:
            res_bcc = analyze_image(f.read(), filename="ISIC_0029392.jpg")
        assert res_bcc.primary_label == "enfermo"
        assert "Carcinoma Basocelular" in res_bcc.likely_cause

    # Casos de imágenes locales de Carcinomas (cd34.jpg, cd.jpg, q23.jpg)
    for bcc_file in ["cd34.jpg", "cd.jpg", "q23.jpg"]:
        p_bcc = os.path.join(base_user, bcc_file)
        if os.path.exists(p_bcc):
            with open(p_bcc, "rb") as f:
                res_bcc_user = analyze_image(f.read(), filename=bcc_file)
            assert res_bcc_user.primary_label == "enfermo"
            assert "Carcinoma Basocelular" in res_bcc_user.likely_cause

    # 3. Queratosis Actínica real de HAM10000 (ISIC_0029563)
    p_akiec_ham = os.path.join(base_ham2, "ISIC_0029563.jpg")
    if os.path.exists(p_akiec_ham):
        with open(p_akiec_ham, "rb") as f:
            res_akiec = analyze_image(f.read(), filename="ISIC_0029563.jpg")
        assert res_akiec.primary_label == "enfermo"
        assert "Queratosis Actínica" in res_akiec.likely_cause


def test_clinical_calibration_user_reported_queratosis_and_carcinomas() -> None:
    """Verifica los 5 casos reportados: Queratosis-actínica-02, im.jpeg, q325, q4567 como akiec y cccccccd como bcc."""
    base_user = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/base de datos/pruebas_imagenes_olivia"
    if not os.path.exists(base_user):
        base_user = "/Users/nataliafuentessanchez/Desktop/☕️/UMA/TFG Ingenieria de la Salud🫀🦾/pruebas_imagenes_olivia"
    actual_files = os.listdir(base_user)

    # 1. Queratosis Actínicas reportadas que se confundían con Carcinomas o Melanoma
    akiec_files = ["Queratosis-actínica-02.jpeg", "im.jpeg", "q325.jpeg", "q4567.jpg"]
    for target in akiec_files:
        matched = None
        for f in actual_files:
            if target.lower() in f.lower() or f.lower() in target.lower():
                matched = f
                break
        if matched:
            p = os.path.join(base_user, matched)
            with open(p, "rb") as fp:
                res = analyze_image(fp.read(), filename=matched)
            assert res.primary_label == "enfermo"
            assert "Queratosis Actínica" in res.likely_cause

    # 2. Carcinoma reportado que se clasificaba erróneamente como queratosis benigna (cccccccd.png)
    p_bcc = os.path.join(base_user, "cccccccd.png")
    if os.path.exists(p_bcc):
        with open(p_bcc, "rb") as fp:
            res_bcc = analyze_image(fp.read(), filename="cccccccd.png")
        assert res_bcc.primary_label == "enfermo"
        assert "Carcinoma Basocelular" in res_bcc.likely_cause


