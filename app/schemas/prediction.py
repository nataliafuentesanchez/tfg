# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    filename: str = Field(..., description="Nombre del archivo procesado")
    primary_label: str = Field(..., description="sano o enfermo")
    severity: str = Field(..., description="ninguno, bajo, medio o peligro")
    benign_malignant: str = Field(..., description="benigno_probable o maligno_probable")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    referral: bool = Field(..., description="Si requiere derivacion al dermatologo")
    likely_cause: str = Field(..., description="Causa visual estimada y patologia compatible")
    recommendation: str = Field(..., description="Mensaje de apoyo para decision clinica")
    user_report: str = Field(..., description="Informe explicativo en lenguaje natural")
    disclaimer: str = Field(..., description="Aviso de no diagnostico")
    abcde_analysis: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Desglose de criterios clinicos ABCDE (Asimetria, Borde, Color, Diametro, Estructura)"
    )
