# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PhototypeInfo(BaseModel):
    fitzpatrick_type: str = Field(..., description="Denominación en escala Fitzpatrick (e.g. 'Fototipo IV')")
    fitzpatrick_scale: str = Field(..., description="Número romano o identificador (e.g. 'IV')")
    ita_angle: float = Field(..., description="Ángulo de Tipología Individual en grados")
    skin_category: str = Field(..., description="Categoría descriptiva de la piel (e.g. 'Piel Morena Clara / Mediterránea')")
    burn_tendency: str = Field(..., description="Facilidad de quemadura solar (e.g. 'Baja / Ocasional')")
    tan_tendency: str = Field(..., description="Capacidad de bronceado (e.g. 'Rápido y progresivo')")
    clinical_description: str = Field(..., description="Descripción clínica de reactividad actínica")
    sun_protection_advice: str = Field(..., description="Recomendaciones personalizadas de fotoprotección")
    recommended_spf: str = Field(..., description="Factor de Protección Solar sugerido (e.g. 'FPS 30 - 50')")


class AnalysisResponse(BaseModel):
    filename: str = Field(..., description="Nombre del archivo procesado")
    primary_label: str = Field(..., description="sano o enfermo")
    severity: str = Field(..., description="ninguno, bajo, medio o grave")
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
    image_base64: Optional[str] = Field(
        default=None,
        description="Imagen analizada codificada en Base64 para inclusion en PDF"
    )
    gradcam_image_base64: Optional[str] = Field(
        default=None,
        description="Mapa de atencion visual e interpretabilidad Grad-CAM codificado en Base64"
    )
    phototype: Optional[PhototypeInfo] = Field(
        default=None,
        description="Estimación del fototipo cutáneo Fitzpatrick (ITA) y recomendaciones de prevención solar"
    )
