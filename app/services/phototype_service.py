# =============================================================================
# AnalisisImagenes — Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import math
import cv2
import numpy as np
from typing import Optional
from app.schemas.prediction import PhototypeInfo


class PhototypeService:
    """
    Servicio de estimación clínica del Fototipo Cutáneo de Fitzpatrick
    mediante el estándar dermatológico computacional ITA (Individual Typology Angle)
    en el espacio de color perceptualmente uniforme CIELAB.
    """

    @staticmethod
    def estimate_phototype(
        image_bgr: np.ndarray,
        lesion_mask: Optional[np.ndarray] = None
    ) -> PhototypeInfo:
        """
        Estima el fototipo cutáneo a partir del fondo de piel sana perilesional.

        Fórmula científica oficial (Chardon et al., 1991 / Del Bino et al., 2014):
        ITA = arctan((L* - 50) / b*) * (180 / pi)
        donde L* es la luminosidad y b* representa el componente amarillo/melánico en CIELAB.
        """
        if image_bgr is None or image_bgr.size == 0:
            return PhototypeService._fallback_phototype()

        h, w = image_bgr.shape[:2]
        if h < 10 or w < 10:
            return PhototypeService._fallback_phototype()

        # 1. Segmentación de píxeles candidatos a piel perilesional sana
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # Descartar viñeteado negro de dermatoscopio, artefactos y brillos especulares saturados
        valid_range = (gray >= 35) & (gray <= 245)

        # Anillo perimetral exterior (la piel periférica suele estar libre de la lesión central)
        border_h = max(int(h * 0.15), 2)
        border_w = max(int(w * 0.15), 2)
        border_mask = np.zeros((h, w), dtype=bool)
        border_mask[:border_h, :] = True
        border_mask[-border_h:, :] = True
        border_mask[:, :border_w] = True
        border_mask[:, -border_w:] = True

        if lesion_mask is not None and lesion_mask.shape == (h, w):
            healthy_skin_mask = valid_range & (lesion_mask == 0)
        else:
            healthy_skin_mask = valid_range & border_mask

        # Si el anillo periférico no tiene suficientes píxeles (ej. recorte muy cerrado), usar toda la zona válida fuera de lesión
        if np.sum(healthy_skin_mask) < 64:
            if lesion_mask is not None and lesion_mask.shape == (h, w):
                healthy_skin_mask = valid_range & (lesion_mask == 0)
            else:
                healthy_skin_mask = valid_range

        if np.sum(healthy_skin_mask) < 32:
            return PhototypeService._fallback_phototype()

        # 2. Conversión a espacio CIELAB
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        # En OpenCV, L está en [0..255] (L* = L * 100 / 255) y b está centrado en 128 (b* = b - 128)
        l_channel = lab[:, :, 0][healthy_skin_mask].astype(np.float64)
        b_channel = lab[:, :, 2][healthy_skin_mask].astype(np.float64)

        l_star = l_channel * (100.0 / 255.0)
        b_star = b_channel - 128.0

        median_l = float(np.median(l_star))
        median_b = float(np.median(b_star))

        # Evitar división por cero
        if abs(median_b) < 1e-4:
            median_b = 1e-4 if median_b >= 0 else -1e-4

        # 3. Cálculo del Ángulo de Tipología Individual (ITA)
        ita = math.atan2(median_l - 50.0, median_b) * (180.0 / math.pi)
        ita = round(ita, 1)

        # 4. Clasificación según la escala oficial de Fitzpatrick / ITA
        return PhototypeService._classify_fitzpatrick(ita)

    @staticmethod
    def _classify_fitzpatrick(ita: float) -> PhototypeInfo:
        """
        Mapea el ángulo ITA a la escala oficial de fototipos Fitzpatrick I a VI.
        """
        if ita > 55.0:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo I",
                fitzpatrick_scale="I",
                ita_angle=ita,
                skin_category="Piel Muy Clara / Albina o Pelirroja",
                burn_tendency="Extrema (siempre se quema intensamente)",
                tan_tendency="Nula (nunca se broncea, propensión a pecas)",
                clinical_description=(
                    "Piel con muy baja concentración de eumelanina y predominio de feomelanina. "
                    "Vulnerabilidad crítica al daño actínico y fotoenvejecimiento prematuro."
                ),
                sun_protection_advice=(
                    "Fotoprotección máxima diaria con FPS 50+ de amplio espectro (UVA/UVB y luz visible). "
                    "Reaplicar cada 2 horas y tras cada baño. Uso indispensable de sombrero de ala ancha, "
                    "gafas con filtro UV400 y ropa protectora UPF. Evitar la exposición solar directa entre las 11:00 y las 16:30 h."
                ),
                recommended_spf="FPS 50+ (Muy Alta)"
            )
        elif ita > 41.0:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo II",
                fitzpatrick_scale="II",
                ita_angle=ita,
                skin_category="Piel Clara / Caucásica Nórdica",
                burn_tendency="Muy alta (se quema con gran facilidad)",
                tan_tendency="Mínima (adquiere un bronceado muy suave y lento)",
                clinical_description=(
                    "Piel clara altamente sensible a la radiación ultravioleta. "
                    "Elevado riesgo acumulativo de eritemas, lentigos solares y queratosis actínicas."
                ),
                sun_protection_advice=(
                    "Uso riguroso de protector solar FPS 50+ en rostro y zonas expuestas los 365 días del año. "
                    "Evitar sesiones de bronceado directo. Sombrero y gafas homologadas en exteriores, "
                    "y autoexploración periódica de lunares según la regla ABCDE."
                ),
                recommended_spf="FPS 50+ (Muy Alta)"
            )
        elif ita > 28.0:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo III",
                fitzpatrick_scale="III",
                ita_angle=ita,
                skin_category="Piel Clara a Media / Centroeuropea - Mediterráneo Claro",
                burn_tendency="Moderada (se quema al inicio de exposición)",
                tan_tendency="Gradual (se broncea progresivamente hacia un tono dorado)",
                clinical_description=(
                    "Piel con capacidad defensiva media frente a la radiación UV. "
                    "Aunque tiene mayor tolerancia que los fototipos I y II, el daño en el ADN celular se acumula de forma silenciosa."
                ),
                sun_protection_advice=(
                    "Aplicar protector FPS 30 a 50 antes de actividades al aire libre. "
                    "Reaplicar cada 2 horas en verano. Mantener hidratación cutánea post-solar y "
                    "no descuidar la protección en días nublados o primaverales."
                ),
                recommended_spf="FPS 30 - 50 (Alta)"
            )
        elif ita > 10.0:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo IV",
                fitzpatrick_scale="IV",
                ita_angle=ita,
                skin_category="Piel Morena Clara / Mediterránea - Hispana",
                burn_tendency="Baja (rara vez se quema con exposición habitual)",
                tan_tendency="Rápida y uniforme (adquiere un bronceado dorado/oscuro con facilidad)",
                clinical_description=(
                    "Piel rica en eumelanina protectora con baja frecuencia de quemaduras inmediatas. "
                    "No obstante, presenta propensión a discromías, manchas hiperpigmentadas, melasma y daño actínico a largo plazo."
                ),
                sun_protection_advice=(
                    "Fotoprotección facial y corporal con FPS 30 a 50 para prevenir melasma y envejecimiento actínico. "
                    "Especial atención en rostro, cuello y manos. Evitar exposiciones solares prolongadas sin reaplicación de filtro."
                ),
                recommended_spf="FPS 30 - 50 (Alta)"
            )
        elif ita > -30.0:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo V",
                fitzpatrick_scale="V",
                ita_angle=ita,
                skin_category="Piel Morena Oscura / Oriente Medio - Sudeste Asiático - Latina",
                burn_tendency="Muy baja (excepcionalmente se quema)",
                tan_tendency="Muy rápida e intensa (se broncea con facilidad y profundidad)",
                clinical_description=(
                    "Alta protección natural frente al eritema solar gracias a la densidad de pigmento melánico. "
                    "Riesgo primario de hiperpigmentación postinflamatoria y lesiones en zonas acrales (palmas y plantas)."
                ),
                sun_protection_advice=(
                    "Protector solar FPS 30-50 de textura ligera o toque seco con filtros frente a luz visible y azul. "
                    "Autoexamen rutinario de zonas poco pigmentadas de forma natural: palmas de las manos, plantas de los pies y lechos ungueales."
                ),
                recommended_spf="FPS 30 - 50 (Antipolución / Luz Visible)"
            )
        else:
            return PhototypeInfo(
                fitzpatrick_type="Fototipo VI",
                fitzpatrick_scale="VI",
                ita_angle=ita,
                skin_category="Piel Negra / Fuertemente Pigmentada",
                burn_tendency="Excepcional (prácticamente nunca sufre eritema solar)",
                tan_tendency="Profundamente pigmentada de base",
                clinical_description=(
                    "Máxima concentración basal de eumelanina fotoprotectora. "
                    "El melanoma fotoinducido por UV es infrecuente; sin embargo, los melanomas en este fototipo suelen presentarse como "
                    "Melanoma Lentiginoso Acral (ALM) en extremidades, requiriendo diagnóstico precoz."
                ),
                sun_protection_advice=(
                    "Fotoprotección hidratante fluida FPS 30+ para prevenir manchas y deshidratación. "
                    "Revisión dermatológica preventiva periódica focalizada en palmas, plantas de los pies, espacios interdigitales y uñas."
                ),
                recommended_spf="FPS 30+ (Prevención Acral y Discromías)"
            )

    @staticmethod
    def _fallback_phototype() -> PhototypeInfo:
        return PhototypeInfo(
            fitzpatrick_type="Fototipo III",
            fitzpatrick_scale="III",
            ita_angle=32.0,
            skin_category="Piel Media / Intermedia (Estimación estándar)",
            burn_tendency="Moderada",
            tan_tendency="Gradual",
            clinical_description=(
                "Estimación clínica estándar ante imagen con fondo cutáneo reducido. "
                "Piel con tolerancia moderada a la radiación solar y necesidad de fotoprotección preventiva."
            ),
            sun_protection_advice=(
                "Uso recomendado de protector solar FPS 30 a 50 en exposición al aire libre. "
                "Reaplicar cada 2 horas y evitar las horas centrales del día."
            ),
            recommended_spf="FPS 30 - 50"
        )

