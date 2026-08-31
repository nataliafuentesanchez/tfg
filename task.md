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

## Pendiente

- [ ] Seleccionar datasets definitivos para entrenamiento (ISIC, HAM10000, PAD-UFES-20)
- [ ] Definir fase 2 con termografia (si hay datos suficientes)
- [ ] Endurecer evaluacion clinica del modelo (priorizar sensibilidad en casos de riesgo)
- [ ] Publicar push remoto en GitHub (falta autenticacion local)
- [ ] Cerrar la calibracion final de umbrales y mascara antes de entrenar modelo supervisado

## Completado

- [x] Fase /spec validada
- [x] Fase /plan validada
- [x] Build inicial funcional con tests pasando
- [x] Versionado local `v.0.1.2`
- [x] Aplicacion verificada en navegador en `http://127.0.0.1:8000/`
- [x] Endpoint `/health` validado con respuesta `{"status":"ok"}`
- [x] Pruebas relevantes ejecutadas: `5 passed in 1.01s`

## Snapshot de Contexto

- Fecha: 2026-08-31
- Estado exacto: la aplicacion esta ejecutandose correctamente en localhost y la fase actual es de calibracion del algoritmo sobre datos reales antes de entrenar un modelo supervisado.
- Bloqueo actual: no es tecnico sino metodologico; el sistema mejora pero aun necesita una ultima afinacion de lesion/fondo y umbrales para reducir falsos positivos.
- Proximo paso exacto: cerrar la calibracion final y, si sigue siendo insuficiente, pasar a una etapa supervisada con features extraidas y validacion train/test.
