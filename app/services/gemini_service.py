# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# SDK de Google Gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GEMINI_SDK_AVAILABLE = False


OLIVIA_SYSTEM_PROMPT = """
Eres la Dra. Olivia, una médica dermatóloga joven de aproximadamente 30 años, muy agradable, gentil, simpática, empática y profesional.
Trabajas como la asistente conversacional del sistema de orientación dermatológica asistido por Inteligencia Artificial (desarrollado para el Trabajo de Fin de Grado de la UMA).

Tu misión principal es:
1. Crear un espacio abierto, seguro y de confianza donde el usuario pueda conversar libremente contigo sobre cualquier duda médica de su piel, síntomas cotidianos (como picor, ardor, cambios de color, lunares nuevos, etc.), antecedentes familiares o dudas generales de salud cutánea.
2. Explicarle de manera muy clara, cercana y comprensible qué significa el análisis dermatológico realizado por nuestro modelo de visión computacional (ResNet-18) cuando hay un informe disponible.
3. Guiar al paciente con tranquilidad y empatía, educándolo sobre la salud de la piel y la prevención.

Normas estrictas de tu comportamiento:
- Mantén siempre una actitud cálida, amable y positiva como una doctora joven entusiasta y rigurosa.
- Habla en español natural, fluido y empático. Usa formato Markdown (negritas, listas con viñetas) para facilitar la lectura.
- Si hay un informe clínico adjunto en el contexto, respeta estrictamente la evaluación de la ResNet-18: explica la patología detectada, la regla ABCDE y el nivel de gravedad sin contradecir ni minimizar el riesgo indicado por el modelo visual.
- Responde a cualquier pregunta que te formule el usuario (sobre patologías como melanoma, queratosis, carcinomas, lunares, síntomas, señales de alerta, cuidados de la piel, etc.) con precisión didáctica, amabilidad y de forma completa.
- Asegúrate de que todas tus respuestas sean totalmente concluidas, auto-contenidas y bien estructuradas. Nunca dejes una frase, idea o lista a la mitad.
- Transmite calma y seguridad, pero mantén un recordatorio profesional sutil de que, aunque eres una IA avanzada de apoyo académico, la valoración presencial por un médico especialista en dermatología es siempre la referencia definitiva para cualquier tratamiento o diagnóstico final.
"""


def _get_gemini_client() -> Optional[Any]:
    load_dotenv(override=True)
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key or not GEMINI_SDK_AVAILABLE:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        logger.warning(f"Error al inicializar cliente de Gemini API: {exc}")
        return None


def generate_olivia_response(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    analysis_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, List[str], str]:
    """
    Genera la respuesta conversacional de la Dra. Olivia conectando con la API de Google Gemini.
    Retorna una tupla: (texto_respuesta, lista_preguntas_sugeridas, estado)
    """
    client = _get_gemini_client()

    # Preparamos el contexto estructurado si existe un informe de la ResNet-18
    context_text = ""
    if analysis_context:
        diag = analysis_context.get("diagnóstico_principal", {})
        sev = analysis_context.get("gravedad", {})
        abcde = analysis_context.get("regla_abcde", {})
        deriv = analysis_context.get("derivacion", {})
        
        context_text = (
            "\n--- CONTEXTO DEL INFORME DERMATOLÓGICO ACTUAL ---\n"
            f" Patología sospechosa: {diag.get('etiqueta_es', 'No especificado')} ({diag.get('codigo', '')})\n"
            f" Confianza técnica: {diag.get('confianza_porcentaje', 0):.1f}%\n"
            f" Nivel de Riesgo / Gravedad: {sev.get('nivel', '').upper()} - {sev.get('descripcion', '')}\n"
            f" Severidad estimada: {sev.get('porcentaje_gravedad', 0)}%\n"
            f" Recomendación de Derivación: {deriv.get('prioridad', '')} -> {deriv.get('mensaje', '')}\n"
            f" Resumen ABCDE: Asimetría ({abcde.get('asimetria', '')}), Bordes ({abcde.get('bordes', '')}), "
            f"Color ({abcde.get('color', '')}), Diámetro ({abcde.get('diametro', '')}), Evolución ({abcde.get('evolucion', '')})\n"
            "--------------------------------------------------\n"
        )

    # Si tenemos conexión con Gemini API
    if client is not None:
        # Probamos con varios modelos en cascada por si alguno experimenta alta demanda temporal (error 503)
        candidate_models = [
            os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
            "gemini-2.5-flash",
            "gemini-flash-latest"
        ]

        prompt_contents = [OLIVIA_SYSTEM_PROMPT]
        if context_text:
            prompt_contents.append(context_text)

        if history:
            prompt_contents.append("\n--- HISTORIAL DE CONVERSACIÓN RECIENTE ---")
            for item in history[-6:]:
                sender = "Paciente" if item.get("sender") == "user" else "Dra. Olivia"
                prompt_contents.append(f"{sender}: {item.get('text', '')}")

        prompt_contents.append(f"\nPaciente: {user_message}\nDra. Olivia:")
        full_prompt = "\n".join(prompt_contents)

        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.9,
                        max_output_tokens=2048,
                    )
                )

                if response and response.text:
                    reply_text = response.text.strip()
                    suggested_chips = _generate_suggested_questions(user_message, analysis_context)
                    return reply_text, suggested_chips, "ok"

            except Exception as err:
                logger.warning(f"Modelo {model_name} no disponible temporalmente: {err}")

    # Fallback conversacional inteligente (cuando no hay API Key o falla la red)
    return _generate_fallback_response(user_message, analysis_context)


def _generate_suggested_questions(user_message: str, analysis_context: Optional[Dict[str, Any]]) -> List[str]:
    """Genera 3 preguntas sugeridas (Quick Chips) dinámicas según el tema consultado."""
    msg_lower = user_message.lower()

    if "melanoma" in msg_lower or "factor" in msg_lower or "riesgo" in msg_lower:
        return [
            "¿Cuáles son los factores de riesgo del melanoma?",
            "¿Cómo se diferencia un lunar de un melanoma?",
            "¿Qué hacer si detecto un lunar sospechoso?"
        ]
    elif "alerta" in msg_lower or "abcde" in msg_lower or "lunar" in msg_lower:
        return [
            "¿Qué significa la A de Asimetría?",
            "¿Cada cuánto debo revisar mis lunares?",
            "¿Qué causa el picor en las manchas de la piel?"
        ]
    elif analysis_context:
        diag_name = analysis_context.get("diagnóstico_principal", {}).get("etiqueta_es", "mi lesión")
        return [
            f"¿Qué cuidados debo tener con {diag_name}?",
            "¿Por qué es importante la regla ABCDE?",
            "¿Qué preguntas le hago al dermatólogo en la cita?"
        ]
    
    return [
        "¿Qué es un melanoma?",
        "¿Cuáles son las señales de alerta en un lunar?",
        "¿Qué causa el picor en las manchas de la piel?"
    ]


def _generate_fallback_response(
    user_message: str, analysis_context: Optional[Dict[str, Any]]
) -> Tuple[str, List[str], str]:
    """Base de conocimiento empática y completa de la Dra. Olivia para responder a cualquier consulta clínica."""
    msg_lower = user_message.lower()

    # 1. Lunar precancerígeno / atípico / displásico
    if "precancer" in msg_lower or "precancerigeno" in msg_lower or "displasico" in msg_lower or "atipico" in msg_lower:
        reply = (
            "Un **lunar precancerígeno** (también conocido como *lunar atípico* o *nevo displásico*) es una lesión benigna en la piel "
            "que presenta características morfológicas inusuales pero que aún no es un cáncer de piel. 😊\n\n"
            "**Características principales:**\n"
            "• **Aspecto:** Suelen ser más grandes que un lunar común (>6 mm), con bordes poco definidos y mezclas de tonos (marrón, rosado o negro).\n"
            "• **Riesgo:** Aunque la mayoría nunca se transforman en cáncer, las personas con múltiples lunares atípicos tienen un riesgo mayor de desarrollar melanoma a lo largo de su vida.\n"
            "• **Prevención:** Es vital vigilarlos mediante la regla **ABCDE** (Asimetría, Bordes, Color, Diámetro y Evolución) y acudir al dermatólogo ante cualquier cambio de forma o tamaño.\n\n"
            "¿Has notado un lunar específico con estas características que quieras que evaluemos?"
        )

    # 1b. Factores de riesgo del melanoma
    elif "factor" in msg_lower or "riesgo" in msg_lower or ("causa" in msg_lower and "melanoma" in msg_lower):
        reply = (
            "¡Es una excelente pregunta! Saber cuáles son los **factores de riesgo del melanoma** es el primer paso para cuidar nuestra piel de forma consciente y preventiva. 😊\n\n"
            "Los principales factores de riesgo reconocidos en dermatología son:\n\n"
            "1. **Exposición a la radiación ultravioleta (UV):** Quemaduras solares acumuladas (especialmente en la infancia/adolescencia) y el uso de camas de bronceado artificial.\n"
            "2. **Tipo de piel (Fototipo claro):** Piel clara, ojos claros, cabello rubio o pelirrojo y presencia de pecas, ya que producen menos melanina protectora.\n"
            "3. **Número y tipo de lunares:** Tener más de 50 lunares comunes o presencia de lunares atípicos (displásicos).\n"
            "4. **Antecedentes familiares y genéticos:** Tener familiares de primer grado (padres, hermanos) diagnosticados de melanoma.\n"
            "5. **Sistema inmunitario debilitado:** Pacientes inmunodeprimidos o con tratamientos inmunosupresores.\n\n"
            "Si presentas varios de estos factores, es muy recomendable realizar una revisión dermatológica anual."
        )

    # 2. Melanoma en general
    elif "melanoma" in msg_lower:
        reply = (
            "El **Melanoma** es el tipo más grave de cáncer de piel. Se origina cuando los melanocitos "
            "(las células que producen la melanina) comienzan a crecer de forma descontrolada. 😊\n\n"
            "**Puntos clave que debes conocer:**\n"
            "• **Aspecto habitual:** Suele parecer un lunar de forma asimétrica, con bordes irregulares, variaciones de color "
            "(marrón, negro, rojo o azulado) y un diámetro mayor a 6 mm.\n"
            "• **Regla ABCDE:** Es la herramienta principal para detectarlo a tiempo (Asimetría, Bordes, Color, Diámetro y Evolución).\n"
            "• **Detección precoz:** Si se diagnostica en etapas tempranas, la tasa de curación supera el 95%.\n\n"
            "Si has notado un lunar nuevo o cambios en uno antiguo, lo más recomendable es programar una consulta con tu dermatólogo."
        )

    # 3. Señales de alerta / Regla ABCDE / Lunares
    elif "alerta" in msg_lower or "abcde" in msg_lower or "señal" in msg_lower or "senales" in msg_lower:
        reply = (
            "La **Regla ABCDE** es el método internacional para valorar si un lunar requiere revisión médica: 😊\n\n"
            "• **A - Asimetría:** Si trazaras una línea por la mitad, las dos partes no coinciden.\n"
            "• **B - Bordes:** Bordes deshilachados, irregulares o poco definidos.\n"
            "• **C - Color:** Variaciones de tono en la misma lesión (marrón, negro, rojizo, azul o blanco).\n"
            "• **D - Diámetro:** Lesiones mayores a 6 mm (tamaño de la goma de un lápiz).\n"
            "• **E - Evolución:** Cualquier cambio rápido de tamaño, forma, color, sangrado o picor.\n\n"
            "¿Te gustaría que revisemos algún lunar específico o tienes foto para analizar?"
        )

    # 4. Queratosis (Actínica o Seborreica)
    elif "queratosis" in msg_lower or "akiec" in msg_lower or "bkl" in msg_lower:
        reply = (
            "La **Queratosis** engloba dos tipos muy comunes de lesiones cutáneas: 😊\n\n"
            "1. **Queratosis Actínica:** Lesión escamosa y áspera producida por la exposición solar acumulada a lo largo de los años. Se considera **premaligna**, por lo que es importante que un dermatólogo la valore para tratarla a tiempo.\n"
            "2. **Queratosis Seborreica:** Crecimiento totalmente **benigno**, común con la edad, de aspecto verrugoso o 'pegado' a la piel.\n\n"
            "¿Tu consulta es sobre una mancha rugosa o áspera al tacto?"
        )

    # 5. Carcinoma (Basocelular o Espinocelular)
    elif "carcinoma" in msg_lower or "bcc" in msg_lower:
        reply = (
            "El **Carcinoma Basocelular (BCC)** es el cáncer de piel más frecuente. Suele manifestarse como un "
            "pequeño bulto perlado, rosado o una mancha brillante que puede sangrar o cicatrizar con dificultad. 😊\n\n"
            "**Lo positivo:** Tiene un crecimiento muy lento y rara vez se extiende a otras partes del cuerpo (bajo riesgo de metástasis), "
            "pero requiere tratamiento quirúrgico o tópico prescrito por el dermatólogo para curarlo por completo."
        )

    # 6. Picor / Ardor / Síntomas
    elif "pico" in msg_lower or "ardor" in msg_lower or "molestia" in msg_lower or "sintoma" in msg_lower or "síntoma" in msg_lower:
        reply = (
            "El **picor o prurito** en la piel es una respuesta muy habitual que puede deberse a diversas causas: 😊\n\n"
            "• **Causas benignas comunes:** Sequedad cutánea (xerosis), dermatitis, eccema, irritación o alergia a productos tópicos.\n"
            "• **Signo de atención:** Cuando un lunar antiguo que nunca picaba comienza a picas repentinamente, descamarse o cambiar, es un criterio de evolución (E) que conviene revisar con tu médico.\n\n"
            "¿El picor está en una mancha o lunar específico o es una sensación generalizada?"
        )

    # 7. Saludo / Bienvenida
    elif "hola" in msg_lower or "buenas" in msg_lower or "quien eres" in msg_lower:
        reply = (
            "¡Hola! Soy la **Dra. Olivia**, médica asistencial de orientación dermatológica. Encantada de ayudarte. 😊\n\n"
            "Estoy aquí para escucharte y resolver todas tus dudas sobre síntomas, lunares, manchas de la piel, "
            "prevención o explicaciones de tu análisis dermatológico.\n\n"
            "¿Qué consulta te gustaría realizar hoy?"
        )

    # 8. Si hay informe clínico en contexto
    elif analysis_context and ("informe" in msg_lower or "resultado" in msg_lower or "diagnostico" in msg_lower or "tengo" in msg_lower or "analisis" in msg_lower):
        diag = analysis_context.get("diagnóstico_principal", {}).get("etiqueta_es", "la lesión analizada")
        sev = analysis_context.get("gravedad", {}).get("nivel", "medio")
        reply = (
            f"Con mucho gusto te explico el resultado de tu imagen. Nuestro modelo ha detectado patrones compatibles con **{diag}** "
            f"con un nivel de riesgo estimado **{sev.upper()}**.\n\n"
            "Esta orientación sirve para darte prioridad de consulta médica. Puedes preguntarme sobre los signos ABCDE "
            "o sobre qué cuidados requiere esta patología antes de acudir al dermatólogo."
        )

    # 9. Respuesta médica didáctica general
    else:
        reply = (
            f"Con respecto a tu consulta (*\"{user_message}\"*), como doctora te comento que la piel refleja tanto factores "
            "externos (sol, humedad, cosméticos) como internos. 😊\n\n"
            "Si notas manchas de coloración inusual, bordes irregulares, cambios recientes o descamación, la recomendación "
            "médica es realizar una exploración con dermatoscopio en consulta presencial.\n\n"
            "¿Quieres que comentemos algún síntoma o lunar en detalle?"
        )

    chips = _generate_suggested_questions(user_message, analysis_context)
    return reply, chips, "fallback"
