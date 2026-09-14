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
  - [x] Suite de tests completa validada (13/13 pasando)

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
- [x] Flujo de 2 pasos interactivo idéntico al diseño de referencia (Landing con Esfera + Chat con Botones y Descarga PDF)
- [x] Calibración de gravedad en Melanoma, soporte iOS/iPad, imagen en PDF y nuevo chat (13/13 tests pasando)

## Snapshot de Contexto

- **Fecha:** 2026-09-14 (Día 7 completado)
- **Estado exacto:** Fase 7 completada. El porcentaje de gravedad en Melanoma refleja el riesgo clínico calibrado (e.g. 85-99%), OLIVIA es 100% funcional en iPad e iPhone tanto por red local (`http://192.168.1.59:8000`) como por cámara nativa, los informes PDF incluyen la foto analizada, se puede iniciar un nuevo chat por texto o botón, y se ha añadido la segmentación por ROI focal (`_extract_focal_crop`) que aísla manchas/lunares en fotos macro. Documentación en `README.md` actualizada y 13/13 tests pasando.
- **Próximo paso exacto:** Implementar mapas de calor *Grad-CAM* como capa de interpretabilidad visual convolucional sobre la imagen.
