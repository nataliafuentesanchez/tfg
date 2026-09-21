# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from app.services.gemini_service import generate_olivia_response, _generate_suggested_questions


def test_generate_suggested_questions_without_context():
    chips = _generate_suggested_questions("Hola", None)
    assert isinstance(chips, list)
    assert len(chips) == 3
    assert any("lunar" in c.lower() for c in chips)


def test_generate_suggested_questions_with_context():
    context = {
        "diagnóstico_principal": {"etiqueta_es": "Melanoma"},
        "gravedad": {"nivel": "peligro"},
    }
    chips = _generate_suggested_questions("¿Qué significa esto?", context)
    assert isinstance(chips, list)
    assert len(chips) == 3
    assert any("Melanoma" in c for c in chips)


def test_generate_olivia_response_fallback():
    reply, chips, status = generate_olivia_response("Hola, tengo dudas sobre mi piel")
    assert isinstance(reply, str)
    assert "Dra. Olivia" in reply or "IA" in reply or "dermatólog" in reply.lower() or "piel" in reply.lower()
    assert isinstance(chips, list)
    assert status in ["ok", "fallback"]
