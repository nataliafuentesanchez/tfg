# Registro de Tareas - AnalisisImagenes

## En curso

- [ ] Fase 3 - Construccion
  - [x] API FastAPI (`/`, `/health`, `/analyze`)
  - [x] Motor baseline de analisis dermatologico
  - [x] Informe legible para usuario + JSON tecnico
  - [x] Interfaz visual para demo (CSS/JS en carpetas separadas)
  - [x] Scripts de arranque/parada multiplataforma
  - [ ] Revision y simplificacion del servicio de inferencia

## Pendiente

- [ ] Seleccionar datasets definitivos para entrenamiento (ISIC, HAM10000, PAD-UFES-20)
- [ ] Definir fase 2 con termografia (si hay datos suficientes)
- [ ] Endurecer evaluacion clinica del modelo (priorizar sensibilidad en casos de riesgo)
- [ ] Publicar push remoto en GitHub (falta autenticacion local)

## Completado

- [x] Fase /spec validada
- [x] Fase /plan validada
- [x] Build inicial funcional con tests pasando
- [x] Versionado local `v0.1.0`

## Snapshot de Contexto

- Fecha: 2026-07-24
- Estado exacto: commit local `v.0.1.0` y tag `v0.1.0` creados en rama `master`.
- Bloqueo actual: autenticacion GitHub pendiente para `git push`.
- Proximo paso exacto: ejecutar `git push -u origin master --tags` despues de autenticar credenciales en GitHub.
