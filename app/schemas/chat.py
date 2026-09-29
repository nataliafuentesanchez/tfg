# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessageItem(BaseModel):
    sender: str = Field(..., description="Origen del mensaje: 'user' u 'olivia'")
    text: str = Field(..., description="Contenido textual del mensaje")


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="Mensaje del usuario enviado a Olivia")
    history: Optional[List[ChatMessageItem]] = Field(
        default_factory=list, description="Historial previo de la conversación"
    )
    analysis_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Contexto estructurado del informe dermatológico de ResNet-18"
    )
    brain_memory: Optional[str] = Field(
        default=None,
        description="Resumen condensado de sesiones anteriores — Cerebro persistente de Olivia"
    )


class ChatMessageResponse(BaseModel):
    reply: str = Field(..., description="Respuesta generada por Olivia")
    suggested_questions: List[str] = Field(
        default_factory=list, description="Preguntas rápidas sugeridas para continuar el diálogo"
    )
    status: str = Field(default="ok", description="Estado de la respuesta ('ok' o 'fallback')")
