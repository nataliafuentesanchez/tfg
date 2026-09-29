# Registro de Tareas - AnalisisImagenes

## En curso

- [x] Fase 3 - Construccion
  - [x] API FastAPI (`/`, `/health`, `/analyze`, `/download-report-pdf`)
  - [x] Motor baseline de analisis dermatologico
  - [x] Informe legible para usuario + JSON tecnico
  - [x] Interfaz visual para demo (CSS/JS en carpetas separadas)
  - [x] Scripts de arranque/parada multiplataforma
  - [x] Revision y simplificacion del servicio de inferencia
  - [x] Validacion final del flujo web y del backend
- [x] Fase 5 - Calibración de Triage, Plantilla Oficial y UI Modular
  - [x] Corrección de severidad en Melanoma (GRAVE directo) y Queratosis Actínica (Premaligna / LEVE-MODERADO)
  - [x] Integración de matriz clínica para las 7 patologías de HAM10000
  - [x] Rediseño frontend estructurado por secciones, métricas clave, contexto, ABCDE y derivación
  - [x] Suite completa de tests unitarios e integración validada (11/11 pasando)
- [x] Fase 6 - Flujo Interactivo de 2 Pasos (Esfera Landing + Chat Olivia) y Exportación PDF
  - [x] Landing interactiva con esfera luminosa animada (Paso 1)
  - [x] Chat conversacional con bienvenida automática y análisis en vivo (Paso 2)
  - [x] Soporte dual: captura directa por cámara web y subida de archivos
  - [x] Generador y exportador de informe clínico en PDF formal descargable con ReportLab
  - [x] Fase 7 - Calibración de Gravedad, Soporte Móvil iPad/iPhone, Foto en PDF y Nuevo Chat
  - [x] Recalibración del porcentaje de gravedad en Melanoma (reflejando el riesgo clínico efectivo e.g. 85-99%)
  - [x] Fallback automático a cámara nativa en iOS/iPadOS sobre conexiones HTTP y activación de entrada de texto
  - [x] Inclusión visual de la fotografía de la lesión enviada por el usuario en el informe clínico PDF descargable
  - [x] Comando conversacional ("quiero abrir un nuevo chat") y botón directo `+ Nuevo Chat` en cabecera
- [x] Fase 8 - Agente Conversacional Inteligente OLIVIA (Google Gemini API)
  - [x] Especificación de personalidad (médica dermatóloga joven ~30 años, empática, gentil y profesional)
  - [x] Actualización de especificaciones y arquitectura (`SPECIFICATIONS.md` y `ARCHITECTURE.md`)
  - [x] Implementación de `app/services/gemini_service.py` con `google-genai` y fallback determínico
  - [x] Creación de esquemas `ChatMessageRequest` y `ChatMessageResponse` (`app/schemas/chat.py`)
  - [x] Endpoint backend `POST /chat` en `app/api/routes.py`
  - [x] Conexión frontend en `app/static/js/app.js` con chips de preguntas sugeridas y conversación abierta fluida
  - [x] Suite de tests unitarios e integración validada (18/18 pasando)

- [x] Fase 9 - Cerebro Persistente, Drawer Slide-In, Recalibración Melanoma y Documentación SDD
  - [x] Cerebro de Olivia real: `buildBrainMemorySummary()` + campo `brain_memory` en schema + inyección en prompt Gemini
  - [x] Panel lateral historial con animación slide-in estilo ChatGPT (CSS transform + class-based toggle)
  - [x] Triage melanoma recalibrado: umbral mel_prob 0.25→0.12, regla emergencia ABCDE multi-criterio, penalización domain-shift CNN benigno vs ABCDE atípico
  - [x] README.md completamente reescrito (v0.2.1)
  - [x] docs/SPECIFICATIONS.md actualizado a /ship v0.2.0 con todos los requisitos confirmados
  - [x] CHANGELOG.md con entrada v0.2.1
  - [x] docs/diario_codigo.md Día 9 completo
  - [x] Suite 18/18 tests pasando

- [x] Fase 10 - Optimización de UX, Latencia Conversacional, Chats Independientes y Gemini-Style Drawer (v0.2.2)
  - [x] Vía rápida de saludos ultra-rápida (<10ms) en `gemini_service.py`
  - [x] Corrección de modelos de Gemini (eliminación de timeout 404 por nombre no válido)
  - [x] Apertura de barra lateral de conversaciones al pulsar el avatar de Olivia
  - [x] Chats nuevos 100% independientes y limpios (eliminación de bocadillos de bienvenida duplicados)
  - [x] Eliminación de la insignia `🧠 Cerebro & Historial` de la cabecera
  - [x] Documentación actualizada en `CHANGELOG.md`, `diario_codigo.md` (Día 10) y `task.md`
  - [x] Suite de 18/18 tests pasando al 100%
- [x] Fase 11 - Eliminación Total de Respuestas Evasivas y Motor de Conocimiento Dermatológico Completo (v0.2.3)
  - [x] Eliminación completa de la plantilla genérica estática evasiva ("Con respecto a tu consulta...")
  - [x] Motor de conocimiento ampliado para marcas post-acné, peticiones de foto, dermatofibroma, rosácea, dermatitis, queratosis, lesiones vasculares, psoriasis y manchas
  - [x] Sintetizador Clínico Experto para cualquier consulta o caso clínico hipotético no catalogado
  - [x] Corrección de variable `GEMINI_MODEL=gemini-2.5-flash` en `.env`
  - [x] Documentación en `CHANGELOG.md` (v0.2.3) y `diario_codigo.md` (Día 10 parte 2)
  - [x] Suite de 18/18 tests pasando al 100%

- [x] Fase 12 - Diagnóstico y Conexión en Vivo con Endpoints Oficiales de Gemini API (v0.2.4)
  - [x] Diagnóstico en tiempo real de la API de Google Gemini: identificados errores 404 en nombres de modelo deprecados.
  - [x] Actualización de la lista prioritaria `candidate_models` a los endpoints oficiales de producción: `gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`.
  - [x] Actualización de `.env` a `GEMINI_MODEL=gemini-flash-lite-latest`.
  - [x] Verificado con script directo: `STATE: ok` (Conexión 100% viva con Gemini AI respondiendo en directo a cualquier consulta libre del usuario).
  - [x] Cobertura adicional para piel grasa (toque seco/oil control), filtros minerales vs químicos y lista de 5 preguntas para el dermatólogo.
  - [x] Documentación en `CHANGELOG.md` (v0.2.4), `diario_codigo.md` (Día 10 parte 3) y `task.md`.
  - [x] Suite de 18/18 tests pasando al 100%.

## Context Snapshot

- **Versión Actual:** `v0.2.4` (OLIVIA AI - TFG UMA)
- **Servidor Activo:** Uvicorn en `http://127.0.0.1:8000/` (Tarea daemon `task-475`)
- **Estado de Tests:** 18/18 pasando (100% pass)
- **Últimos Cambios:** Conexión en vivo 100% activa con el endpoint oficial `gemini-flash-lite-latest` (`STATE: ok`), resolviendo cualquier pregunta libre de dermatología al instante.

## Pendiente

- [ ] Mapas de atención visual (Grad-CAM) para explicabilidad convolucional
- [ ] Generar curvas ROC-AUC multiclase para incluir en el anexo de la memoria
- [ ] Definir fase 2 con termografia (si hay datos suficientes)
- [ ] Publicar push remoto en GitHub (falta autenticacion local)

## Benchmark real validado (ResNet-18 en HAM10000 Test Set - 1.494 imágenes)

- **Fecha:** 2026-09-07
- **Dataset:** HAM10000 (10.015 imagenes con metadatos reales, split por lesion_id).
- **Métricas Triage Clínico Binario (Derivación Maligna vs Seguimiento Benigno):**
  - **Accuracy:** `81.39%`
  - **Sensibilidad / Recall en Malignos:** `78.62%` (vs ~59% del baseline heurístico)
  - **Precisión en Benignos:** `93.42%`
- **Métricas Multiclase (7 patologías dermatológicas):**
  - **Accuracy Global:** `74.03%`
  - **Macro F1:** `0.6081` (vs 0.48 del baseline heurístico)
  - **Recall por patología:**
    - Vascular (`vasc`): `100.0%`
    - Nevus Melanocítico (`nv`): `76.41%`
    - Carcinoma Basocelular (`bcc`): `73.53%`
    - Queratosis Actínica (`akiec`): `71.43%`
    - Queratosis Benigna (`bkl`): `69.08%`
    - Melanoma (`mel`): `63.64%`
    - Dermatofibroma (`df`): `71.43%`

## Completado

- [x] Fase /spec validada
- [x] Fase /plan validada
- [x] Build inicial funcional con tests pasando
- [x] Versionado local `v.0.1.2`
- [x] Aplicacion verificada en navegador en `http://127.0.0.1:8000/`
- [x] Endpoint `/health` validado con respuesta `{"status":"ok"}`
- [x] Red Neuronal Convolucional (ResNet-18) entrenada, guardada e integrada
- [x] Triage clínico depurado, plantilla estandarizada y UI modular por tarjetas
- [x] Flujo de 2 pasos interactivo (Landing con Esfera + Chat con Botones y Descarga PDF)
- [x] Calibración de gravedad en Melanoma, soporte iOS/iPad, imagen en PDF y nuevo chat
- [x] Integración Google Gemini en Chatbot OLIVIA (18/18 tests pasando)
- [x] Cerebro persistente real, drawer animado, melanoma recalibrado, docs actualizadas (v0.2.1)

## Snapshot de Contexto

- **Fecha:** 2026-09-29 (Fase 9 completada — v0.2.1)
- **Estado exacto:** v0.2.1 operativa. El Cerebro de Olivia es ahora memoria real inyectada en el prompt de Gemini. El drawer tiene animación slide-in estilo ChatGPT. El triage de melanoma usa triple capa de seguridad clínica (umbral mel_prob 0.12, emergencia ABCDE multi-criterio, penalización domain-shift). README, SPECIFICATIONS, CHANGELOG y diario_codigo actualizados. 18/18 tests pasando.
- **Próximo paso:** Implementar Grad-CAM para mapas de atención visual (interpretabilidad convolucional) o iniciar la fase de escritura de la memoria del TFG.
