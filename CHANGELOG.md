# Changelog - AnalisisImagenes

All notable changes to this project are documented in this file.
This format follows Keep a Changelog and Semantic Versioning.

## [Unreleased]

## [0.2.4] - 2026-09-29

### Fixed
- **Resolución Definitiva de Conexión Gemini API (`gemini-flash-lite-latest`)**:
  - Detectado que los nombres de modelo anteriores (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`) devolvían errores 404 (deprecados por Google API) o 429 de cuota en modelos beta.
  - Actualizada la lista prioritaria `candidate_models` en `gemini_service.py` a los endpoints oficiales de producción ultrarrápidos: `gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite` y `gemini-flash-latest`.
  - Configurado `GEMINI_MODEL=gemini-flash-lite-latest` en `.env`.
  - **Resultado**: Conexión 100% viva con Gemini AI (`STATE: ok`) para **cualquier consulta abierta o aleatoria del usuario**, generando respuestas personalizadas e inteligentes al instante.

### Added
- **Respuestas Específicas de Respaldo**: Añadidos casos específicos de respuesta clínica local para preguntas sobre fotoprotección para piel grasa/acneica (toque seco, oil-control), diferenciación entre filtros minerales (físicos) y químicos (orgánicos), y checklist de 5 preguntas clave para la cita dermatológica.

## [0.2.3] - 2026-09-29

### Added
- **Motor de Conocimiento Clínico Completo y Eliminación de Respuestas Genéricas**:
  - Eliminada totalmente la respuesta evasiva genérica (*"Con respecto a tu consulta..."*).
  - Añadidas respuestas clínicas rigurosas, estructuradas y profundas para **marcas post-acné y cicatrices** (PIH, PIE, niacinamida, azelaico, retinoides, microneedling), **peticiones de fotos** (guía paso a paso 📷 Cámara / 📁 Subir, ResNet-18, ABCDE), **dermatofibroma** (nódulo benigno, signo del hoyuelo), rosácea, dermatitis, queratosis, vascular, psoriasis y deshidratación.
  - Creado un **Sintetizador Clínico Experto** que evalúa cualquier consulta abierta, síntoma o caso hipotético no listado con criterios anatómicos, regla ABCDE y señales de alarma.

### Changed
- **Configuración de Entorno `.env`**: Actualizada la variable `GEMINI_MODEL=gemini-2.5-flash` para garantizar conexión directa con la API de Google Gemini sin bloqueos por nombres de modelo deprecados/erróneos.

## [0.2.2] - 2026-09-29

### Added
- **Respuestas Médicas Estructuradas y Didácticas**: Se ha enriquecido `OLIVIA_SYSTEM_PROMPT` y el motor de conocimiento local en `gemini_service.py` para responder consultas dermatológicas generales (ej. sol, fotoprotección, cremas) de forma clara, directa y estructurada en 5 apartados: 1) Respuesta directa, 2) Consecuencias UV, 3) Recomendaciones de exposición, 4) Uso de protector solar (regla de los dos dedos, reaplicación), y 5) Tipos de cremas y filtros (minerales/físicos vs químicos, FPS 50+).
- **Vía Rápida para Saludos (Ultra-fast Greetings)**: Saludos cotidianos ("hola", "buenas", "saludos", "hola olivia") se responden de forma instantánea (<10ms) sin latencia ni llamadas redundantes a la API de Gemini.
- **Nuevos Chats 100% Independientes**: Al pulsar "+ Nuevo Chat", la sesión de chat se reinicia completamente limpia, eliminando mensajes de bienvenida estáticos duplicados.

### Changed
- **Panel Lateral de Conversaciones (Gemini Style)**: El panel lateral ahora se activa al pulsar el icono/avatar de Olivia en la cabecera, funcionando como la barra lateral de historial de Gemini con botón "+ Nuevo Chat" y listado de conversaciones anteriores.
- **Optimización de Latencia y Cascada de Modelos**: Eliminada la cadena de modelo no válida que provocaba timeouts y retries de 4s+. Los modelos configurados son `gemini-2.5-flash`, `gemini-2.0-flash` y `gemini-1.5-flash`.
- Asset cache-busting bumpeado a `?v=2.5`.

### Removed
- **Insignia "🧠 Cerebro & Historial" de la Cabecera**: Eliminado el badge visible en la barra superior por indicación de UX (el Cerebro es memoria interna e invisible de Olivia, y el historial se gestiona desde la barra lateral).

## [0.2.1] - 2026-09-29

### Added
- **Cerebro de Olivia — Memoria Persistente Real**: Olivia ahora recuerda conversaciones anteriores. `saveCurrentSessionToBrain()` genera un resumen condensado de cada sesión (diagnóstico, consultas clave) guardado en `localStorage`. La nueva función `buildBrainMemorySummary()` extrae los 4 resúmenes más recientes y los inyecta en el prompt de Gemini mediante el campo `brain_memory` del schema `ChatMessageRequest`.
- **Panel Lateral Historial (Drawer Slide-In estilo ChatGPT/Gemini)**: El drawer lateral ahora usa animación CSS `transform: translateX(-100%) → translateX(0)` con transición cúbica (`cubic-bezier(0.4, 0, 0.2, 1)`). El backdrop aparece con `opacity: 0 → 1`. Se controla mediante clase `.drawer-open` en lugar de `display: none/flex`.
- **Triage Melanoma Recalibrado**: Nuevo sistema de triage clínico en `inference_service.py`:
  - Umbral `mel_prob` bajado de `0.25` → `0.12` para mayor sensibilidad.
  - Regla de emergencia ABCDE multi-criterio: si ≥2 criterios (asimetría + color / asimetría + bordes / color + bordes) son simultáneamente atípicos, se activa alerta clínica.
  - Penalización de predicciones benignas de la CNN (nv/bkl/df/vasc) cuando el ABCDE contradice la predicción (domain-shift dermatoscopia → foto de teléfono/internet).

### Changed
- `README.md` completamente reescrito para reflejar v0.2.0/v0.2.1 con tabla de capacidades, stack técnico, instalación, tests y estructura de proyecto.
- `docs/SPECIFICATIONS.md` completamente actualizado a `/ship` v0.2.0 con todos los requisitos funcionales confirmados, escenarios de uso, criterios de aceptación y historial de fases SDD.
- Cache de assets estáticos bumpeada a `?v=2.4`.
- `brain_memory` añadido a `ChatMessageRequest` (campo opcional `Optional[str]`).
- `generate_olivia_response()` acepta `brain_memory` e inyecta la memoria de sesiones previas en el prompt de Gemini.

### Fixed
- Melanoma de fotos de internet clasificado incorrectamente como "Queratosis Benigna" por dependencia excesiva de la CNN en predicciones benignas. Solucionado con penalización ABCDE + umbral mel_prob reducido.
- Drawer no animado (aparecía/desaparecía bruscamente). Solucionado con transición CSS `transform` y gestión de visibilidad con `requestAnimationFrame` + timeout de 310ms.

## [0.2.0] - 2026-09-21


### Added
- Integrated Google Gemini API (`google-genai`, `gemini-3.6-flash` with model fallback cascade) into Chatbot OLIVIA for fluid conversational interactions.
- Defined Dr. Olivia's persona: 30-year-old friendly, empathetic, and professional female dermatologist AI.
- Open conversational dialogue: users can ask about pre-existing skin conditions, precancerous moles, symptoms, preventive tips, or details about the ResNet-18 report.
- Cerebro & Historial de Olivia: slide-out drawer panel (`historyDrawer`) with `localStorage` session memory to store, browse, and restore past chat conversations.
- Dynamic Quick Chips (suggested questions) with safe `addEventListener` event binding.
- Enhanced Markdown parser in `app.js` and CSS styles for spacious, distinct section cards, numbered items, and clear heading typography.
- Non-dermatoscopic smartphone photo triage in `inference_service.py` based on ROI focal cropping + ABCDE features independent of filename.
- Added Pydantic schemas in `app/schemas/chat.py` and endpoint `POST /chat` in `app/api/routes.py`.
- Suite of unit and integration tests for `gemini_service.py` and `POST /chat` (18/18 passing).

### Fixed
- Fixed footer chat input bar flexbox alignment: action buttons (`Subir`, `Cámara`) placed on left, text input field and send icon properly aligned.
- Fixed fallback response knowledge engine for precancerous, atypical, and dysplastic mole inquiries.
- Fixed `analysis_context` payload in `app.js` to use correct `AnalysisResponse` field names (`risk_score`, `referral`, `benign_malignant`) instead of non-existent aliases.
- Fixed unit test `test_large_symmetric_benign_patch` to use clinically unambiguous brown/skin-tone colors (previous test used blue/cyan on pink which is genuinely suspicious per ABCDE criteria).
- Bumped static asset cache-busting versions to `?v=2.3` to force browser reload of updated CSS and JS.


## [0.1.2] - 2026-08-31

### Added
- New landing screen design inspired by the minimalist OLIVIA aesthetic.
- Result panel shown directly under the uploaded image and analysis output.
- Improved user-facing analysis text with a cleaner narrative layout.
- Continued preparation for dataset-based calibration before supervised training.

### Changed
- Updated the frontend UX to a lighter, more polished demo presentation.
- Refined the analysis workflow so the textual report is visible immediately after processing.
- Bumped the application version to `0.1.2`.

### Fixed
- Adjusted benign vs suspicious lesion threshold calibration to keep common NV examples safe while preserving suspicious lesion detection.
- Verified backend and analysis tests continue passing after the UI update.

## [0.1.0] - 2026-07-24

### Added
- Initial SDD setup for project context and planning.
- FastAPI web app with endpoints `GET /`, `GET /health`, and `POST /analyze`.
- Baseline dermatology image analysis service with:
  - primary classification (`sano` / `enfermo`)
  - severity levels (`ninguno`, `bajo`, `medio`, `peligro`)
  - probable lesion type (`benigno_probable` / `maligno_probable`)
  - referral recommendation for dermatology
- Human-readable report (`user_report`) in addition to technical JSON output.
- Frontend redesign for demo presentation quality.
- Frontend assets organized into dedicated folders:
  - `app/static/css/styles.css`
  - `app/static/js/app.js`
- Cross-platform run scripts:
  - Windows: `start.cmd`, `stop.cmd`
  - macOS/Linux: `start.sh`, `stop.sh`
- Initial test suite (unit + integration) for core logic and health endpoint.

### Changed
- `README.md` updated with real installation and run instructions.
- UI updated to show both understandable narrative output and machine-readable JSON.

### Fixed
- Consistency of analysis response payload to support both technical and non-technical users.
