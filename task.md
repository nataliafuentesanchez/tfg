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
- [x] Fase 5 - Calibración de Triage, Plantilla Oficial y UI Modular
  - [x] Corrección de severidad en Melanoma (GRAVE directo) y Queratosis Actínica (Premaligna / LEVE-MODERADO)
  - [x] Integración de matriz clínica para las 7 patologías de HAM10000
  - [x] Rediseño frontend estructurado por secciones, métricas clave, contexto, ABCDE y derivación
  - [x] Suite completa de tests unitarios e integración validada (11/11 pasando)

## Pendiente

- [ ] Fase 6: Mapas de atención visual (Grad-CAM) para explicabilidad convolucional
- [ ] Generador y exportador de informe clínico en PDF descargable
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
- [x] Pruebas completas ejecutadas: `11 passed in 2.54s`

## Snapshot de Contexto

- **Fecha:** 2026-09-07 (Día 5 completado)
- **Estado exacto:** La aplicación cuenta con inferencia ResNet-18 calibrada con la matriz clínica de 7 patologías de HAM10000. Los informes web se presentan modularizados en 4 secciones visuales (Métricas, Contexto, ABCDE y Recomendación/Derivación).
- **Próximo paso exacto (Día 6):** Implementar mapas de atención visual (*Grad-CAM*) para que el usuario pueda visualizar exactamente la región de la lesión que activó la sospecha de la red neuronal.

