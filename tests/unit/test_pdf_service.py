# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from app.services.pdf_service import generate_clinical_pdf


def test_generate_clinical_pdf() -> None:
    sample_data = {
        "filename": "ISIC_0025964.jpg",
        "primary_label": "enfermo",
        "severity": "grave",
        "benign_malignant": "maligno_probable",
        "risk_score": 0.85,
        "likely_cause": "Melanoma",
        "recommendation": "Se recomienda programar una consulta dermatológica urgente.",
        "abcde_analysis": {
            "asymmetry_score": 0.42,
            "asymmetry_desc": "Asimetría marcada (alta sospecha)",
            "border_score": 0.38,
            "border_desc": "Bordes irregulares",
            "color_score": 0.35,
            "color_desc": "Heterogeneidad cromática",
            "diameter_score": 0.45,
            "diameter_desc": "Diámetro significativo"
        }
    }
    pdf_bytes = generate_clinical_pdf(sample_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_clinical_pdf_with_phototype() -> None:
    sample_data = {
        "filename": "ISIC_0025964.jpg",
        "primary_label": "enfermo",
        "severity": "grave",
        "benign_malignant": "maligno_probable",
        "risk_score": 0.90,
        "likely_cause": "Melanoma",
        "recommendation": "Se recomienda consulta urgente.",
        "phototype": {
            "fitzpatrick_type": "Fototipo IV",
            "fitzpatrick_scale": "IV",
            "ita_angle": 22.5,
            "skin_category": "Piel Morena Clara / Mediterránea",
            "burn_tendency": "Baja",
            "tan_tendency": "Rápida y uniforme",
            "clinical_description": "Piel mediterránea.",
            "sun_protection_advice": "FPS 30-50 diario.",
            "recommended_spf": "FPS 30 - 50"
        }
    }
    pdf_bytes = generate_clinical_pdf(sample_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")



def test_generate_clinical_pdf_with_image() -> None:
    # 1x1 pixel PNG en base64
    tiny_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    sample_data = {
        "filename": "ISIC_0025964.jpg",
        "primary_label": "enfermo",
        "severity": "grave",
        "benign_malignant": "maligno_probable",
        "risk_score": 0.95,
        "likely_cause": "Melanoma",
        "recommendation": "Se recomienda consulta urgente.",
        "image_base64": tiny_b64
    }
    pdf_bytes = generate_clinical_pdf(sample_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_clinical_pdf_with_phototype() -> None:
    sample_data = {
        "filename": "ISIC_0025964.jpg",
        "primary_label": "enfermo",
        "severity": "grave",
        "benign_malignant": "maligno_probable",
        "risk_score": 0.90,
        "likely_cause": "Melanoma",
        "recommendation": "Se recomienda consulta urgente.",
        "phototype": {
            "fitzpatrick_type": "Fototipo IV",
            "fitzpatrick_scale": "IV",
            "ita_angle": 22.5,
            "skin_category": "Piel Morena Clara / Mediterránea",
            "burn_tendency": "Baja",
            "tan_tendency": "Rápida y uniforme",
            "clinical_description": "Piel mediterránea.",
            "sun_protection_advice": "FPS 30-50 diario.",
            "recommended_spf": "FPS 30 - 50"
        }
    }
    pdf_bytes = generate_clinical_pdf(sample_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")

