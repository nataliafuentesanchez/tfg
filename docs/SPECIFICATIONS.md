# 📋 Especificaciones: OLIVIA AI — Orientación Dermatológica

> **Versión:** `v0.2.0`  
> **Fase SDD:** `/ship` — Versión 0.2.0 completada y validada  
> **Última Revisión:** 2026-09-29  
> **Autora:** Natalia Fuentes Sánchez · TFG Ingeniería de la Salud · UMA  
> **Metodología:** Spec-Driven Development (dbv-specs-ops)

---

## 🎯 1. Contexto y Objetivos

- **Problema:** [CONFIRMADO] Se necesita un sistema de apoyo para analizar imágenes médicas dermatológicas que permita detectar patrones compatibles con cáncer de piel, priorizar casos de riesgo y proporcionar orientación médica accesible al usuario.
- **Objetivo (Éxito):** [CONFIRMADO] Sistema funcional que clasifique imágenes dermatológicas en 7 patologías, estime gravedad clínica, proporcione un informe PDF descargable, y ofrezca orientación conversacional empática mediante la Dra. Olivia (Google Gemini LLM).

---

## 👥 2. Usuarios y Escenarios

- **Perfil de Usuario:** [CONFIRMADO] Pacientes o personas preocupadas por lesiones cutáneas, investigadora del TFG (Natalia), tutor/a académico y personal clínico como revisores secundarios.
- **Escenarios Clave:**
  - *Escenario A:* [CONFIRMADO] Subir fotografía dermatológica (profesional o de teléfono móvil) y recibir informe clínico con clasificación de riesgo, ABCDE y recomendación de derivación.
  - *Escenario B:* [CONFIRMADO] Conversar libremente con la Dra. Olivia sobre síntomas, lunares, manchas, factores de riesgo o cualquier duda de salud cutánea.
  - *Escenario C:* [CONFIRMADO] Olivia recuerda conversaciones anteriores (Cerebro persistente) y personaliza la experiencia a lo largo del tiempo.
  - *Escenario D:* [CONFIRMADO] Recuperar y explorar sesiones de conversación previas mediante el panel lateral (Historial de Chats).
  - *Escenario E:* [CONFIRMADO] Descargar informe clínico en PDF con imagen de la lesión, diagnóstico ABCDE completo y derivación recomendada.

---

## ✨ 3. Funcionalidades Principales (Requisitos)

- [x] **Clasificación clínica primaria:** [CONFIRMADO] Clasifica cada imagen como `sano` o `enfermo`.
  - **Criterio de aceptación:** El sistema devuelve etiqueta primaria, probabilidad por clase, nivel ABCDE y patología más compatible.
- [x] **Estratificación de gravedad:** [CONFIRMADO] Para casos enfermos, clasifica gravedad en `ninguno`, `bajo`, `medio` o `grave`.
  - **Criterio de aceptación:** Devuelve nivel de gravedad con umbrales documentados y risk_score calibrado [0.0 – 1.0].
- [x] **Subclasificación 7 patologías HAM10000:** [CONFIRMADO] Melanoma (mel), Carcinoma Basocelular (bcc), Queratosis Actínica (akiec), Queratosis Benigna (bkl), Nevus Melanocítico (nv), Dermatofibroma (df), Vascular (vasc).
  - **Criterio de aceptación:** Precisión global > 70%, Macro F1 > 0.55 en test set real de HAM10000.
- [x] **Recomendación de derivación:** [CONFIRMADO] Sugerir derivación al dermatólogo cuando se detecte riesgo clínico.
  - **Criterio de aceptación:** Si el caso es `grave` o `maligno_probable`, el sistema marca prioridad alta de derivación.
- [x] **Evaluación ABCDE (Explainability / XAI):** [CONFIRMADO] Análisis morfológico de Asimetría, Bordes, Color, Diámetro y Estructura/Evolución con scores numéricos y descripciones clínicas.
- [x] **Informe PDF clínico descargable:** [CONFIRMADO] El usuario puede descargar un informe formal en PDF con imagen de la lesión, diagnóstico estructurado y recomendación.
- [x] **Agente Conversacional OLIVIA (Google Gemini API):** [CONFIRMADO] Chatbot conversacional con la API de Google Gemini (`gemini-3.6-flash`).
  - **Perfil de Personalidad:** Médica dermatóloga joven (~30 años), muy agradable, gentil, simpática y profesional. Transmite calidez, calma y confianza.
  - **Conversación Libre Abierta:** El usuario puede realizar preguntas sobre cualquier problema dermatológico, síntoma, duda general o el informe de la ResNet-18 en todo momento.
  - **Sugerencia Proactiva:** Olivia sugiere preguntas relevantes (Quick Chips) de forma natural para orientar al paciente.
  - **Fallback Empático:** Si la API no está disponible, motor de respuestas local basado en conocimiento clínico dermatológico.
  - **Límites Éticos:** Mantiene recordatorio profesional de que es una IA de apoyo, no reemplaza al especialista.
- [x] **Cerebro de Olivia (Memoria Persistente Cross-Session):** [CONFIRMADO] Olivia recuerda sesiones anteriores del usuario y construye un contexto acumulativo que inyecta en el prompt de Gemini para personalizar la interacción.
  - **Implementación:** `localStorage` + `buildBrainMemorySummary()` → campo `brain_memory` en `ChatMessageRequest` → inyectado en prompt de Gemini.
  - **Criterio de aceptación:** En una nueva sesión, si hay sesiones previas, Olivia puede mostrar continuidad natural en la conversación.
- [x] **Panel Historial de Chats (Drawer Lateral):** [CONFIRMADO] Panel lateral deslizante (slide-in desde la izquierda, estilo ChatGPT/Gemini) accesible mediante el avatar de Olivia en la cabecera.
  - **Contenido:** Lista de sesiones anteriores con título, fecha y número de mensajes. Botones de "Nuevo Chat" e "Inicio" dentro del panel.
  - **Criterio de aceptación:** El panel se abre con animación suave, muestra el historial y permite restaurar cualquier sesión.
- [x] **Triage Autónomo de Imágenes No Profesionales:** [CONFIRMADO] El sistema analiza imágenes tomadas con teléfono móvil o descargadas de internet sin depender del nombre del archivo.
  - **Mecanismo:** ROI Focal Crop + ABCDE multi-criterio + penalización de predicciones benignas de la CNN cuando el ABCDE contradice.

---

## 🏗️ 4. Arquitectura Técnica (Resumen)

- **Backend:** FastAPI + Uvicorn. Endpoints: `GET /`, `GET /health`, `POST /analyze`, `POST /chat`, `POST /download-report-pdf`.
- **Visión:** ResNet-18 entrenada en HAM10000 (10.015 imágenes, 7 clases). Triage dual: inferencia completa + ROI focal crop. Análisis ABCDE morfológico.
- **LLM:** Google Gemini API (`google-genai`). Cascada de modelos: `gemini-3.6-flash` → `gemini-2.5-flash` → `gemini-flash-latest`.
- **Memoria:** Campo `brain_memory` en schema + inyección en prompt de Gemini.
- **Frontend:** HTML5 + Vanilla CSS + JavaScript. Drawer con animación CSS (`transform: translateX`).

---

## 🚫 5. Fuera de Alcance

- [x] [CONFIRMADO] Diagnóstico médico definitivo o sustitución del criterio dermatológico.
- [x] [CONFIRMADO] Integración hospitalaria real (HIS/EHR).
- [ ] [PENDIENTE] Mapas de atención visual Grad-CAM (previsto para v0.3.0).
- [ ] [PENDIENTE] Termografía dermatológica (fase 2 futura).
- [ ] [PENDIENTE] Publicación en producción con autenticación de usuario.

---

## ⚠️ 6. Riesgos y Mitigación

- **Riesgo:** Dominio-shift entre imágenes dermatoscópicas (entrenamiento) y fotos de teléfono móvil (uso real).
  - **Mitigación:** [CONFIRMADO] Regla de emergencia ABCDE multi-criterio + penalización de predicciones benignas de la CNN cuando los criterios morfológicos son contradictorios.
- **Riesgo:** Error 503/404 de la API de Gemini por alta demanda.
  - **Mitigación:** [CONFIRMADO] Cascada de 3 modelos candidatos con fallback al motor local si todos fallan.
- **Riesgo clínico y regulatorio:** Sobre-interpretación del sistema como diagnóstico definitivo.
  - **Mitigación:** [CONFIRMADO] Disclaimer permanente en UI y en todas las respuestas de Olivia. Informe PDF incluye aviso médico-legal.

---

## 🧪 7. Criterios de Evaluación

- [x] **Métricas de Modelo ResNet-18:** Accuracy 74.03%, Macro F1 0.6081, Sensibilidad malignos 78.62%, Precisión benignos 93.42%.
- [x] **Suite de Tests:** 18/18 tests pasando (unit + integration).
- [x] **Calidad Conversacional Olivia:** Respuestas completas, empáticas y bien estructuradas (Markdown).
- [x] **UX:** Interfaz funcional en escritorio, móvil e iPad (responsive).

---

## 📋 8. Historial de Fases SDD

| Fase | Estado | Fecha |
|---|---|---|
| `/spec` v1 | ✅ Completada | 2026-07-24 |
| `/plan` v1 | ✅ Completada | 2026-07-24 |
| `/build` v0.1.0 | ✅ Completada | 2026-07-24 |
| `/build` v0.1.2 | ✅ Completada | 2026-08-31 |
| `/build` v0.2.0 | ✅ Completada | 2026-09-21 |
| `/ship` v0.2.0 | ✅ Completada | 2026-09-29 |

---

**Instrucción para la IA:** Este documento está en fase `/ship` para v0.2.0. Cualquier nueva funcionalidad debe iniciar una nueva fase `/spec` antes de comenzar implementación.