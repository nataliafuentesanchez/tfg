# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_endpoint_basic():
    payload = {
        "message": "Hola Dra. Olivia, tengo un lunar nuevo",
        "history": [],
        "analysis_context": None
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "suggested_questions" in data
    assert isinstance(data["suggested_questions"], list)
    assert data["status"] in ["ok", "fallback"]


def test_chat_endpoint_with_analysis_context():
    payload = {
        "message": "¿Por qué es importante este resultado?",
        "history": [
            {"sender": "user", "text": "Hola"},
            {"sender": "olivia", "text": "¡Hola! ¿En qué puedo ayudarte?"}
        ],
        "analysis_context": {
            "diagnóstico_principal": {
                "etiqueta_es": "Melanoma",
                "codigo": "mel",
                "confianza_porcentaje": 92.5
            },
            "gravedad": {
                "nivel": "peligro",
                "descripcion": "Riesgo alto de malignidad",
                "porcentaje_gravedad": 92
            },
            "regla_abcde": {
                "asimetria": "Marcada",
                "bordes": "Irregulares",
                "color": "Heterogéneo",
                "diametro": ">6mm",
                "evolucion": "Cambio rápido"
            },
            "derivacion": {
                "prioridad": "Alta",
                "mensaje": "Derivación urgente a dermatología"
            }
        }
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
