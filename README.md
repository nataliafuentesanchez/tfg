# AnalisisImagenes

Aplicacion web para apoyo al analisis dermatologico mediante vision por computador.
El sistema recibe una imagen y devuelve:
- clasificacion primaria (`sano` o `enfermo`)
- nivel de gravedad (`ninguno`, `bajo`, `medio`, `peligro`)
- estimacion (`benigno_probable` o `maligno_probable`)
- recomendacion de derivacion clinica

## Aviso importante

Este proyecto es de apoyo academico (TFG) y no sustituye el diagnostico medico profesional.

## Stack tecnico

- Python 3.11+
- FastAPI + Uvicorn
- OpenCV + Numpy
- Pytest

## Ejecucion rapida

### Windows

```cmd
start.cmd
```

### macOS / Linux

```bash
./start.sh
```

Aplicacion disponible en:

http://127.0.0.1:8000/

## Parar la aplicacion

### Windows

```cmd
stop.cmd
```

### macOS / Linux

```bash
./stop.sh
```

## Tests

```bash
python -m pytest -q
```

## Estructura principal

```text
/
|- app/
|  |- api/
|  |- schemas/
|  |- services/
|  |- static/
|     |- css/
|     |- js/
|- tests/
|  |- unit/
|  |- integration/
|- docs/
|- requirements.txt
|- start.cmd
|- stop.cmd
|- start.sh
|- stop.sh
```

## Documentacion del proyecto

- Especificaciones funcionales: `docs/SPECIFICATIONS.md`
- Arquitectura tecnica: `docs/ARCHITECTURE.md`
- Diseno de interfaz: `docs/DESIGN.md`
- Plan de iteracion: `implementation_plan.md`
- Historial de cambios: `CHANGELOG.md`
