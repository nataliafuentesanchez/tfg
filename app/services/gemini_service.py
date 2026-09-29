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
1. Responder de forma DIRECTA, ESPECÍFICA y EXCLUSIVA a la duda concreta formulada por el usuario.
2. Centrar tu respuesta ÚNICAMENTE en el tema específico consultado (acné, piel grasa, manchas, lunares, rosácea, tipo de filtro, preguntas para la cita, etc.).

Normas estrictas de tu comportamiento y estilo:
- NUNCA incluyas bloques de recomendaciones de exposición solar, reglas de la crema solar, ni tipos de filtros a menos que el usuario pregunte EXPRESAMENTE sobre el sol, fotoprotección o hábitos de crema solar.
- Responde siempre de manera concisa, clara y enfocada al punto desde la primera frase.
- Estructura tu respuesta utilizando un formato Markdown limpio y elegante (subtítulos ### solo si aportan valor, negritas y viñetas).
- Mantén un tono cálido, humano, profesional y empático.
- Asegúrate de que todas tus respuestas sean auto-contenidas, totalmente concluidas y adaptadas exactamente a la pregunta realizada.
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
    brain_memory: Optional[str] = None,
) -> Tuple[str, List[str], str]:
    """
    Genera la respuesta conversacional de la Dra. Olivia conectando con la API de Google Gemini.
    Retorna una tupla: (texto_respuesta, lista_preguntas_sugeridas, estado)
    brain_memory: Resumen condensado de sesiones anteriores (Cerebro persistente de Olivia).
    """
    msg_clean = user_message.strip().lower()
    is_greeting = msg_clean in {
        "hola", "buenas", "buenos dias", "buenas tardes", "buenas noches",
        "hey", "saludos", "hola olivia", "hola dra. olivia", "hola dra olivia",
        "hola!", "hola, olivia", "hola buenas", "hola, buenas", "hola!"
    } or (len(msg_clean) <= 12 and any(w in msg_clean for w in ["hola", "buenas", "saludos", "hey"]))

    # ⚡ VÍA RÁPIDA DE ULTRA-ALTA VELOCIDAD PARA SALUDOS SIMPLES
    if is_greeting and not analysis_context:
        reply = (
            "¡Hola! 👋 Soy la **Dra. Olivia**, tu médica asistencial de orientación dermatológica. ¡Encantada de saludarte! 😊\n\n"
            "Estoy aquí para ayudarte con cualquier duda sobre tu piel, síntomas, prevención o para analizar las fotografías de lunares y manchas que subas.\n\n"
            "¿En qué puedo ayudarte hoy?"
        )
        chips = [
            "¿Cuáles son los factores de riesgo del melanoma?",
            "¿Qué es la regla ABCDE?",
            "¿Cómo saber si un lunar es peligroso?"
        ]
        return reply, chips, "ok"

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
        # Lista de modelos activos comprobados de alta velocidad y sin errores 404
        candidate_models = [
            "gemini-flash-lite-latest",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-flash-latest",
            os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")
        ]

        prompt_contents = [OLIVIA_SYSTEM_PROMPT]
        if context_text:
            prompt_contents.append(context_text)

        # Inyeccion del Cerebro de Olivia: memoria de sesiones previas
        if brain_memory and brain_memory.strip():
            prompt_contents.append(
                "\n--- MEMORIA DE SESIONES PREVIAS (Cerebro de Olivia) ---\n"
                "A continuación tienes un resumen de conversaciones anteriores con este paciente. "
                "Úsalo de forma natural para personalizar tu respuesta, mostrar continuidad y empatía, "
                "sin repetirlo literalmente al usuario:\n"
                + brain_memory.strip()
                + "\n------------------------------------------------------\n"
            )

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

    if "sol" in msg_lower or "crema" in msg_lower or "protector" in msg_lower or "fotoprotect" in msg_lower:
        return [
            "¿Cuál es la diferencia entre filtro mineral y químico?",
            "¿Cada cuánto se debe reaplicar el protector solar?",
            "¿Qué cantidad de crema solar debo aplicarme?"
        ]
    elif "melanoma" in msg_lower or "factor" in msg_lower or "riesgo" in msg_lower:
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
        "¿El sol puede ser malo para la piel?",
        "¿Cuáles son las señales de alerta en un lunar?",
        "¿Qué causa el picor en las manchas de la piel?"
    ]


def _generate_fallback_response(
    user_message: str, analysis_context: Optional[Dict[str, Any]]
) -> Tuple[str, List[str], str]:
    """Base de conocimiento empática, rigurosa y completa de la Dra. Olivia para responder a cualquier consulta clínica."""
    msg_lower = user_message.lower()

    # 1. Peticiones de análisis de foto / imagen / cámara
    if "foto" in msg_lower or "imagen" in msg_lower or "camara" in msg_lower or "cámara" in msg_lower or "subir" in msg_lower or "analizar" in msg_lower:
        reply = (
            "¡Por supuesto! Estoy totalmente lista para analizar tu imagen. 📸\n\n"
            "### Instrucciones para enviar tu fotografía:\n"
            "1. **Tomar foto en directo:** Pulsa el botón **📷 Cámara** justo abajo en la barra de herramientas para abrir la cámara de tu dispositivo.\n"
            "2. **Subir imagen guardada:** Pulsa el botón **📁 Subir** para elegir cualquier foto de tu galería o almacenamiento.\n\n"
            "### ¿Qué hará mi sistema de visión por IA?\n"
            "• Nuestra red neuronal convolucional (**ResNet-18**) analizará los patrones morfológicos de la lesión.\n"
            "• Extraeré automáticamente la regla **ABCDE** (Asimetría, Bordes, Color, Diámetro y Evolución).\n"
            "• Te entregaré un nivel de gravedad estimado, recomendación de derivación médica y la opción de descargar tu informe clínico en PDF."
        )

    # 2. Acné, marcas post-acné, manchas rojas o cicatrices
    elif "acne" in msg_lower or "acné" in msg_lower or "marca" in msg_lower or "cicatriz" in msg_lower or "espinilla" in msg_lower or "grano" in msg_lower or "granito" in msg_lower:
        reply = (
            "Las **marcas y cicatrices post-acné** son una consulta muy habitual en dermatología. Ocurren como respuesta a la inflamación previa en el folículo pilosebáceo. Te explico los tipos y tratamientos clave: 😊\n\n"
            "### 1. Tipos de marcas post-acné:\n"
            "• **Eritema post-inflamatorio (marcas rojas/rosadas):** Inflamación vascular persistente tras la curación del grano.\n"
            "• **Hiperpigmentación post-inflamatoria (marcas oscuras/marrones):** Producción localizada en exceso de melanina por los melanocitos.\n"
            "• **Cicatrices atróficas (hoyuelos/picahielo/rolling):** Pérdida de estructura de colágeno en la dermis profunda.\n\n"
            "### 2. Ingredientes y activos cosméticos recomendados:\n"
            "• **Niacinamida (4-5%):** Calma la inflamación, mejora la función barrera y unifica el tono.\n"
            "• **Ácido Azelaico (10-15%):** Excelente acción antiinflamatoria, antibacteriana y despigmentante suave.\n"
            "• **Retinoides (Retinol / Ácido Retinoico):** Estimulan la renovación celular y la síntesis de colágeno.\n"
            "• **Alfa y Beta Hidroxiácidos (Glicólico / Salicílico):** Exfolian suavemente para acelerar la difuminación de manchas.\n\n"
            "### 3. Tratamientos dermatológicos en consulta presencial:\n"
            "• **Peelings químicos médicos, Microneedling (Dermapen) o Láser Fraccionado** para cicatrices con relieve o hundimiento.\n"
            "• **Fotoprotección solar estricta (FPS 50+):** Indispensable diaria para evitar que la radiación UV oscurezca las marcas permanentemente.\n\n"
            "¿Tus marcas son rojas, oscuras o tienen textura/hundimiento?"
        )

    # 3. Dermatofibroma y nódulos cutáneos benignos
    elif "dermatofibroma" in msg_lower or "nodulo" in msg_lower or "nódulo" in msg_lower or "fibroma" in msg_lower:
        reply = (
            "El **Dermatofibroma** (también llamado *histiocitoma fibroso benigno*) es un crecimiento benigno de la piel sumamente común. Te detallo sus características clave: 😊\n\n"
            "### 1. Características clínicas:\n"
            "• **Aspecto:** Suele manifestarse como un pequeño nódulo o bulto firme al tacto, de color rosa, marrón o rojizo.\n"
            "• **Ubicación típica:** Con frecuencia aparece en las piernas o brazos, a menudo tras picaduras de insecto o pequeños traumatismos superficiales.\n"
            "• **Signo del Hoyuelo (Dimple Sign):** Si presionas suavemente los laterales de la lesión con dos dedos, la parte central se hunde ligeramente hacia adentro. Es un hallazgo diagnóstico característico.\n\n"
            "### 2. Manejo y tratamiento:\n"
            "• **Naturaleza 100% Benigna:** No evoluciona a cáncer de piel ni requiere extirpación salvo que cause molestias por roce, picor o razones estéticas.\n"
            "• **Revisión médica:** Ante cualquier cambio de tamaño, dolor agudo o duda diagnóstica, la dermatoscopia presencial confirma de inmediato su patrón fibroso.\n\n"
            "¿Has notado un bulto firme con estas características?"
        )

    # 4. Sol, fotoprotección y cremas solares (Piel Grasa / Toque seco)
    elif "grasa" in msg_lower or "sebo" in msg_lower or "brillo" in msg_lower:
        reply = (
            "Para la **piel grasa o con tendencia acneica**, el protector solar ideal debe ser ultraligero y matificante: 😊\n\n"
            "### 1. Nomenclatura obligatoria en el envase:\n"
            "• **Toque Seco / Dry Touch / Oil-Control:** Formulados para absorber el exceso de sebo y evitar brillos a lo largo del día.\n"
            "• **Oil-Free / Libre de Aceites:** Garantizan que no contengan grasas comedogénicas.\n"
            "• **Non-Comedogenic (No Comedogénico):** No obstruyen los poros ni provocan brotes de granitos o comedones.\n\n"
            "### 2. Texturas recomendadas:\n"
            "• **Fluido acuoso (*Water-fluid* o *Shaka Fluid*):** Se absorben al instante sin dejar rastro blanco ni sensación pesada.\n"
            "• **Gel-Crema Matificante:** Aporta la hidratación justa en gel sin aportar aceite.\n\n"
            "### 3. Activos beneficiosos integrados:\n"
            "• **Niacinamida, Ácido Salicílico o Sílice:** Ayudan a regular el sebo y calmar los poros.\n\n"
            "¿Buscas alguna recomendación de textura para usar antes del maquillaje o a diario?"
        )

    # 4b. Filtros Minerales vs Químicos
    elif "mineral" in msg_lower or "quimico" in msg_lower or "químico" in msg_lower or "filtro" in msg_lower:
        reply = (
            "La diferencia principal entre los **filtros minerales (físicos)** y los **filtros químicos (orgánicos)** radica en cómo interactúan con la radiación solar: 😊\n\n"
            "### 1. Filtros Físicos / Minerales (Óxido de Zinc y Dióxido de Titanio):\n"
            "• **Mecanismo:** Actúan como un 'espejo' sobre la piel, reflejando y rebotando la radiación UV.\n"
            "• **Ventajas:** Acción inmediata al aplicar, no provocan alergias ni picor en los ojos. Son ideales para **pieles sensibles, reactivas, con rosácea, dermatitis o para niños**.\n"
            "• **Inconveniente:** Texturas algo más densas que pueden dejar un ligero rastro blanco si no están micronizados.\n\n"
            "### 2. Filtros Químicos / Orgánicos (Avobenzona, Tinosorb, Octocrylene, etc.):\n"
            "• **Mecanismo:** Absorben los fotones de radiación UV y los transforman en calor inofensivo.\n"
            "• **Ventajas:** Texturas invisibles, ultra-fluidas y toque seco. Ideales para uso urbano y pieles grasas.\n"
            "• **Inconveniente:** Requieren aplicarse 15-20 minutos antes de la exposición y pueden irritar pieles con alergias intensas.\n\n"
            "¿Tu piel suele irritarse fácilmente o prefieres una textura invisible?"
        )

    # 4c. Preguntas para la cita con el dermatólogo
    elif "cita" in msg_lower or "dermatologo" in msg_lower or "dermatólogo" in msg_lower or "pregunta" in msg_lower:
        reply = (
            "Para aprovechar al máximo tu **consulta dermatológica presencial**, te recomiendo llevar preparadas estas 5 preguntas clave: 😊\n\n"
            "1. **Evaluación de lunares:** *¿Hay alguna lesión en mi piel o espalda que requiera seguimiento especial o biopsia?*\n"
            "2. **Diagnóstico preciso:** *¿Cuál es el diagnóstico exacto de esta mancha/nódulo y qué causa su aparición?*\n"
            "3. **Rutina diaria:** *¿Qué ingredientes activos son idóneos para mi fototipo y tipo de piel?*\n"
            "4. **Señales de alerta:** *¿Qué cambios específicos (regla ABCDE) debo vigilar en casa entre revisiones?*\n"
            "5. **Plan de tratamiento:** *¿Cuáles son las opciones de tratamiento (tópico, láser, crioterapia o cirugía) y sus plazos de recuperación?*\n\n"
            "¿Tienes una cita programada próximamente para revisar un lunar o un síntoma específico?"
        )

    # 4d. Sol y fotoprotección general
    elif "sol" in msg_lower or "crema" in msg_lower or "protector" in msg_lower or "fotoprotector" in msg_lower or "broncea" in msg_lower or "uv" in msg_lower:
        reply = (
            "La **fotoprotección solar** es el pilar preventivo más importante en dermatología: 😊\n\n"
            "• **Efectos del sol:** La radiación ultravioleta (UVA/UVB) causa quemaduras solares, fotoenvejecimiento prematuro (arrugas y manchas) y aumenta el riesgo de desarrollar melanoma.\n"
            "• **Recomendación básica:** Utilizar fotoprotector de amplio espectro (FPS 50+) diariamente, reaplicar cada 2 horas si estás al aire libre y evitar la radiación directa entre las 12:00 y las 16:00 horas.\n\n"
            "¿Te gustaría conocer qué textura o tipo de filtro es mejor para tu tipo de piel?"
        )

    # 5. Lunar precancerígeno / atípico / displásico
    elif "precancer" in msg_lower or "precancerigeno" in msg_lower or "precancerígeno" in msg_lower or "displasico" in msg_lower or "displásico" in msg_lower or "atipico" in msg_lower or "atípico" in msg_lower:
        reply = (
            "Un **lunar precancerígeno** (también conocido como *lunar atípico* o *nevo displásico*) es una lesión benigna en la piel "
            "que presenta características morfológicas inusuales pero que aún no es un cáncer de piel. 😊\n\n"
            "**Características principales:**\n"
            "• **Aspecto:** Suelen ser más grandes que un lunar común (>6 mm), con bordes poco definidos y mezclas de tonos (marrón, rosado o negro).\n"
            "• **Riesgo:** Aunque la mayoría nunca se transforman en cáncer, las personas con múltiples lunares atípicos tienen un riesgo mayor de desarrollar melanoma a lo largo de su vida.\n"
            "• **Prevención:** Es vital vigilarlos mediante la regla **ABCDE** (Asimetría, Bordes, Color, Diámetro y Evolución) y acudir al dermatólogo ante cualquier cambio de forma o tamaño.\n\n"
            "¿Has notado un lunar específico con estas características que quieras que evaluemos?"
        )

    # 6. Factores de riesgo del melanoma
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

    # 7. Melanoma en general
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

    # 8. Señales de alerta / Regla ABCDE / Lunares
    elif "alerta" in msg_lower or "abcde" in msg_lower or "señal" in msg_lower or "senales" in msg_lower or "lunar" in msg_lower:
        reply = (
            "La **Regla ABCDE** es el método internacional para valorar si un lunar requiere revisión médica: 😊\n\n"
            "• **A - Asimetría:** Si trazaras una línea por la mitad, las dos partes no coinciden.\n"
            "• **B - Bordes:** Bordes deshilachados, irregulares o poco definidos.\n"
            "• **C - Color:** Variaciones de tono en la misma lesión (marrón, negro, rojizo, azul o blanco).\n"
            "• **D - Diámetro:** Lesiones mayores a 6 mm (tamaño de la goma de un lápiz).\n"
            "• **E - Evolución:** Cualquier cambio rápido de tamaño, forma, color, sangrado o picor.\n\n"
            "¿Te gustaría que revisemos algún lunar específico o tienes foto para analizar?"
        )

    # 9. Queratosis (Actínica o Seborreica)
    elif "queratosis" in msg_lower or "akiec" in msg_lower or "bkl" in msg_lower:
        reply = (
            "La **Queratosis** engloba dos tipos muy comunes de lesiones cutáneas: 😊\n\n"
            "1. **Queratosis Actínica:** Lesión escamosa y áspera producida por la exposición solar acumulada a lo largo de los años. Se considera **premaligna**, por lo que es importante que un dermatólogo la valore para tratarla a tiempo.\n"
            "2. **Queratosis Seborreica:** Crecimiento totalmente **benigno**, común con la edad, de aspecto verrugoso o 'pegado' a la piel.\n\n"
            "¿Tu consulta es sobre una mancha rugosa o áspera al tacto?"
        )

    # 10. Carcinoma (Basocelular o Espinocelular)
    elif "carcinoma" in msg_lower or "bcc" in msg_lower:
        reply = (
            "El **Carcinoma Basocelular (BCC)** es el cáncer de piel más frecuente. Suele manifestarse como un "
            "pequeño bulto perlado, rosado o una mancha brillante que puede sangrar o cicatrizar con dificultad. 😊\n\n"
            "**Lo positivo:** Tiene un crecimiento muy lento y rara vez se extiende a otras partes del cuerpo (bajo riesgo de metástasis), "
            "pero requiere tratamiento quirúrgico o tópico prescrito por el dermatólogo para curarlo por completo."
        )

    # 11. Picor / Ardor / Síntomas
    elif "pico" in msg_lower or "ardor" in msg_lower or "molestia" in msg_lower or "sintoma" in msg_lower or "síntoma" in msg_lower:
        reply = (
            "El **picor o prurito** en la piel es una respuesta muy habitual que puede deberse a diversas causas: 😊\n\n"
            "• **Causas benignas comunes:** Sequedad cutánea (xerosis), dermatitis, eccema, irritación o alergia a productos tópicos.\n"
            "• **Signo de atención:** Cuando un lunar antiguo que nunca picaba comienza a picas repentinamente, descamarse o cambiar, es un criterio de evolución (E) que conviene revisar con tu médico.\n\n"
            "¿El picor está en una mancha o lunar específico o es una sensación generalizada?"
        )

    # 12. Rosácea / Cuperosis / Rojez
    elif "rosacea" in msg_lower or "rosácea" in msg_lower or "cuperosis" in msg_lower or "rojez" in msg_lower or "dermatitis" in msg_lower or "eccema" in msg_lower:
        reply = (
            "Las afecciones vasculares y eritematosas como la **Rosácea** o la **Dermatitis** cursan con sensibilidad cutánea e inflamación. 😊\n\n"
            "### 1. Consejos de cuidado:\n"
            "• **Limpiadores suaves:** Usar syndet sin sulfatos ni fragancias.\n"
            "• **Activos calmantes:** Ácido Azelaico, Niacinamida y Ceramidas.\n"
            "• **Protección solar:** Usar filtros minerales FPS 50+ para evitar el ardor.\n\n"
            "¿Sientes ardor al exponerte al sol o probar cosméticos?"
        )

    # 13. Saludo / Bienvenida
    elif "hola" in msg_lower or "buenas" in msg_lower or "quien eres" in msg_lower:
        reply = (
            "¡Hola! Soy la **Dra. Olivia**, médica asistencial de orientación dermatológica. Encantada de ayudarte. 😊\n\n"
            "Estoy aquí para escucharte y resolver todas tus dudas sobre síntomas, lunares, manchas de la piel, "
            "prevención o explicaciones de tu análisis dermatológico.\n\n"
            "¿Qué consulta te gustaría realizar hoy?"
        )

    # 14. Si hay informe clínico en contexto
    elif analysis_context and ("informe" in msg_lower or "resultado" in msg_lower or "diagnostico" in msg_lower or "tengo" in msg_lower or "analisis" in msg_lower):
        diag = analysis_context.get("diagnóstico_principal", {}).get("etiqueta_es", "la lesión analizada")
        sev = analysis_context.get("gravedad", {}).get("nivel", "medio")
        reply = (
            f"Con mucho gusto te explico el resultado de tu imagen. Nuestro modelo ha detectado patrones compatibles con **{diag}** "
            f"con un nivel de riesgo estimado **{sev.upper()}**.\n\n"
            "Esta orientación sirve para darte prioridad de consulta médica. Puedes preguntarme sobre los signos ABCDE "
            "o sobre qué cuidados requiere esta patología antes de acudir al dermatólogo."
        )

    # 15. Respuesta concisa adaptada para cualquier consulta abierta
    else:
        reply = (
            f"Como **Dra. Olivia**, respondo con gusto a tu consulta (*\"{user_message}\"*): 😊\n\n"
            "En dermatología, las características de la piel dependen de la interacción entre tu tipo cutáneo (fototipo, producción sebácea) y los cuidados diarios.\n\n"
            "Si deseas evaluar una mancha o lunar específico, puedes pulsar el botón **📷 Cámara** o **📁 Subir** para realizar un análisis de visión computacional con nuestra red **ResNet-18**.\n\n"
            "¿Deseas profundizar en algún detalle específico de tu piel?"
        )

    chips = _generate_suggested_questions(user_message, analysis_context)
    return reply, chips, "fallback"
