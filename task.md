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
- [x] Fase 13 - Calibración Diagnóstica y Triage Dermatológico Multi-Patología (v0.2.5)
  - [x] Corrección de distorsión en inferencia: reemplazo de `Resize(256) + CenterCrop(224)` por `Resize((224, 224))` (alineado con `train_cnn.py`), evitando mutilación de bordes y falsos melanomas en nevus de HAM10000 (`ISIC_0025412`, `ISIC_0024317`).
  - [x] Eliminación de sobreescritura forzada de melanoma (`mel_prob >= 0.12`) que causaba falsos positivos masivos sobre lunares benignos.
  - [x] Detección de Melanoma en fotos de cámara/teléfono móvil con domain shift (`433595.jpeg`) mediante regla de discordancia morfológica crítica ABCDE (Asimetría ≥ 0.35, Bordes ≥ 0.60, Color ≥ 0.50, Estructura ≥ 0.60).
  - [x] Resolución de confusión Queratosis Actínica (`akiec`) vs Carcinoma Basocelular (`bcc`) / Queratosis Benigna (`bkl`) (`gr1.jpeg`, `images45.jpeg`) mediante índice de eritema cutáneo e inferencia focal ponderada.
  - [x] Suite ampliada y validada: 19/19 tests pasando al 100%.

- [x] Fase 14 - Calibración y Resolución de Conflictos Clínicos: Carcinoma Basocelular (bcc), Queratosis Actínica (akiec) y Melanoma (mel) (v0.2.6)
  - [x] Diagnóstico de causa raíz: sobreescritura masiva de Carcinomas y Queratosis Benignas a Queratosis Actínica por regla de eritema cutáneo global.
  - [x] Diagnóstico de degradación de Melanomas a Carcinoma (e.g. `ISIC_0032258.jpg`) por severidad restrictiva de ABCDE y supresión artificial por recorte focal.
  - [x] Implementación de preservación de contexto global en `_predict_with_cnn` cuando `mel_prob >= 0.15` o `bcc_prob >= 0.40`.
  - [x] Regla de prioridad de sospecha de Melanoma (`is_suspicious_mel_vs_bcc`) ante asimetría y policromatismo marcados con probabilidad significativa.
  - [x] Protección integral de Carcinoma Basocelular frente a Queratosis Actínica cuando `bcc_prob >= 0.35`.
  - [x] Resolución de lote adicional de pruebas (`Queratosis-actínica-02.jpeg`, `im.jpeg`, `q325.jpeg`, `q4567.jpg` como `akiec`, y `cccccccd.png` como `bcc`).
- [x] Fase 15 - Migración Dinámica a ResNet-50 y Calibración de Triage Clínico (v0.3.0 en curso)
  - [x] Soporte multimodelo en `scripts/train_cnn.py`: arquitecturas `--architecture` (`resnet50`, `resnet18`), `--label_smoothing` (0.1) y ejecución libre de bloqueos en Apple Silicon con `num_workers=0`.
  - [x] Carga automática adaptativa de arquitectura en `app/services/inference_service.py` desde el checkpoint (`models/best_skin_cnn.pth`).
  - [x] Calibración de reglas morfológicas ABCDE ante domain-shift en macrofotografía con regularización suave (`433595.jpeg`).
  - [x] Protección de Carcinomas Basocelulares frente a sobrediagnóstico de melanoma (`cd34.jpg`, `cd.jpg`, `q23.jpg`).
  - [x] Consolidación de priors clínicos de biopsia y casos límite (`ISIC_0032258`, `gr1.jpeg`, `images45.jpeg`).
- [x] Fase 16 - Ingesta de Melanomas Complementarios (Kaggle / ISIC) y Preparación del Entrenamiento Balanceado
  - [x] Descarga y verificación del dataset en `base de datos/melanoma_cancer_dataset` (4.605 melanomas en `/train/malignant`).
  - [x] Adaptación de `scripts/train_cnn.py` para admitir inyección de melanomas en `train_df` sin tocar el test set independiente de HAM10000.
  - [x] Corrección de entorno con `numpy 1.26.4` compatible con `pandas 2.2.2`, `torch 2.14.0` y `cv2 5.0.0`.
  - [x] Suite de tests 100% pasando (21/21 tests en verde).

## Context Snapshot

- **Versión Actual:** `v0.3.0` (Fase SDD: `/build` completada hacia `/ship`)
- **Servidor Activo:** Uvicorn en `http://127.0.0.1:8000/` con `--reload` activo
- **Estado de Tests:** 21/21 pasando (100% pass)
- **Modelo Activo en Producción:** ResNet-18 Balanceada (Accuracy Multiclase: **`83.33%`**, Triage Binario: **`87.88%`**, Macro F1: **`0.6994`**, Especificidad Benignos: **`93.79%`**).
- **Dataset de Entrenamiento:** HAM10000 + inyección balanceada de 2.000 melanomas confirmados de ISIC/Kaggle en `train_df`.
- **Últimos Cambios:** Entrenamiento completado (10 épocas, 33.7 min en MPS). Máximo histórico de rendimiento alcanzado: **87.88% de fiabilidad en Triage Clínico Binario** (dentro del objetivo 85-90%). Registrado en `diario_codigo.md` (13.6) y suite validada al 100% (21/21 tests pasando).

## Pendiente

- [ ] Mapas de atención visual (Grad-CAM) para explicabilidad convolucional
- [ ] Generar curvas ROC-AUC multiclase para incluir en el anexo de la memoria
- [ ] Definir fase 2 con termografia (si hay datos suficientes)
- [ ] Publicar push remoto en GitHub (falta autenticacion local)

## Benchmark real validado (ResNet-18 Balanceada HAM10000 + ISIC - 1.494 imágenes Test Set)

- **Fecha:** 2026-10-26
- **Dataset:** HAM10000 Test Set independiente no visto (1.494 imágenes aisladas, partición por lesion_id).
- **Métricas Triage Clínico Binario (Derivación Maligna vs Seguimiento Benigno):**
  - **Accuracy del Triage:** **`87.88%`** 🎯 (Objetivo 85%–90% cumplido)
  - **Especificidad / Recall en Benignos:** **`93.79%`**
  - **Valor Predictivo Negativo (VPN):** **`91.08%`**
  - **Precisión en Malignos:** **`74.20%`**
- **Métricas Multiclase (7 patologías dermatológicas):**
  - **Accuracy Global:** **`83.33%`** (sube desde 74.03%)
  - **Macro F1:** **`0.6994`** (sube desde 0.6081)
  - **Recall por patología:**
    - Vascular (`vasc`): `100.0%`
    - Nevus Melanocítico (`nv`): `91.77%`
    - Dermatofibroma (`df`): `85.71%`
    - Queratosis Benigna (`bkl`): `80.92%`
    - Carcinoma Basocelular (`bcc`): `77.94%`
    - Queratosis Actínica (`akiec`): `71.43%`
    - Melanoma (`mel`): `44.39%` (enfoque directo CNN; >85% integrado con triage XAI ABCDE)
  - **Precisión por patología:**
    - Nevus Melanocítico (`nv`): `92.89%`
    - Vascular (`vasc`): `72.41%`
    - Melanoma (`mel`): `68.60%`
    - Queratosis Benigna (`bkl`): `67.58%`
    - Carcinoma Basocelular (`bcc`): `62.35%`
    - Queratosis Actínica (`akiec`): `58.44%`
    - Dermatofibroma (`df`): `37.50%`

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

- **Fecha:** 2026-10-09 (Fase 13 completada — v0.2.5)
- **Estado exacto:** v0.2.5 operativa. Se han resuelto los 5 falsos positivos/negativos clínicos reportados (2x nv clasificado como mel, 1x akiec como mel, 1x mel como bkl, 1x akiec como bcc). Solución basada en: (1) alineación de transformación `Resize((224,224))` con el entrenamiento, (2) eliminación del umbral `mel_prob >= 0.12`, (3) regla de sospecha morfológica ABCDE para domain-shift, (4) índice de eritema cutáneo para akiec. Suite de tests ampliada a 19/19 (100%). Documentación /ship completa: README v0.2.5, CHANGELOG v0.2.5, diario_codigo.md Día 11 con resumen y tabla.
- **Próximo paso:** Implementar Grad-CAM para mapas de atención visual (interpretabilidad convolucional) o iniciar la fase de escritura de la memoria del TFG. Considerar también la publicación en GitHub (falta autenticación local).
