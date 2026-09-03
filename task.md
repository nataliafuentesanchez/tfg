# Registro de Tareas - AnalisisImagenes

## En curso

- [x] Fase 3 - Construccion
  - [x] API FastAPI (`/`, `/health`, `/analyze`)
  - [x] Motor baseline de analisis dermatologico
  - [x] Informe legible para usuario + JSON tecnico
  - [x] Interfaz visual para demo (CSS/JS en carpetas separadas)
  - [x] Scripts de arranque/parada multiplataforma
  - [x] Revision y simplificacion del servicio de inferencia
  - [x] Validacion final del flujo web y del backend
- [x] Fase 4 - Deep Learning / Red Neuronal Convolucional (ResNet-18)
  - [x] Integracion y split agrupado por `lesion_id` sobre HAM10000 (10.015 imagenes)
  - [x] Entrenamiento de CNN con Transfer Learning y Loss Ponderada en Apple Silicon MPS
  - [x] Evaluacion en test set independiente (1.494 imagenes)
  - [x] Generacion de matriz de confusion y curvas de aprendizaje para memoria TFG
  - [x] Integracion directa del modelo CNN en `app/services/inference_service.py`
  - [x] Suite completa de tests unitarios e integracion validada (11/11 pasando)

## Pendiente

- [ ] Generar curvas ROC-AUC multiclase para incluir en el anexo de la memoria
- [ ] Definir fase 2 con termografia (si hay datos suficientes)
- [ ] Publicar push remoto en GitHub (falta autenticacion local)

## Benchmark real validado (ResNet-18 en HAM10000 Test Set - 1.494 imágenes)

- **Fecha:** 2026-09-03
- **Dataset:** HAM10000 (10.015 imagenes con metadatos reales, split por lesion_id).
- **Métricas Triage Clínico Binario (Derivación Maligna vs Seguimiento Benigno):**
  - **Accuracy:** `81.39%`
  - **Sensibilidad / Recall en Malignos:** `78.62%` (vs ~59% del baseline)
  - **Precisión en Benignos:** `93.42%`
- **Métricas Multiclase (7 patologías dermatológicas):**
  - **Accuracy Global:** `74.03%`
  - **Macro F1:** `0.6081` (vs 0.48 del baseline)
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
- [x] Pruebas completas ejecutadas: `11 passed in 2.44s`
- [x] Graficos generados en `docs/confusion_matrix_cnn.png` y `docs/training_curves_cnn.png`

## Snapshot de Contexto

- **Fecha:** 2026-09-03
- **Estado exacto:** La aplicación cuenta con una Red Neuronal Convolucional (ResNet-18) entrenada sobre HAM10000 e integrada en la API web. Las predicciones en vivo en el navegador utilizan inferencia de Deep Learning en tiempo real.
- **Próximo paso exacto:** Probar imágenes desde la interfaz web o preparar el capítulo de resultados/metodología para la memoria del TFG con los gráficos generados.
