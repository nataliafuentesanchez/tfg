# OLIVIA AI — Orientación Dermatológica Asistida por Inteligencia Artificial

> **Versión:** v0.3.0 · **TFG Ingeniería de la Salud** · Universidad de Málaga (UMA)  
> **Autora:** Natalia Fuentes Sánchez · **Metodología:** Spec-Driven Development (SDD)

---

## ¿Qué es OLIVIA?

**OLIVIA** es un sistema conversacional de orientación dermatológica asistido por IA diseñado para el Trabajo de Fin de Grado de la UMA. Combina una red neuronal convolucional (soporte dinámico ResNet-50 / ResNet-18) para el análisis visual de lesiones cutáneas con un agente conversacional impulsado por la API de Google Gemini.

La Dra. Olivia actúa como una médica dermatóloga joven de ~30 años: empática, profesional y accesible. El usuario puede hablar libremente con ella, subir fotografías de lesiones para analizarlas, recibir informes clínicos en PDF y recuperar conversaciones anteriores gracias al **Cerebro de Olivia**.

> ⚠️ **Aviso importante:** Esta herramienta es un sistema de apoyo académico y de cribado. No sustituye el diagnóstico médico profesional de un especialista en dermatología.

---

## Capacidades principales (v0.3.0)

| Capacidad | Descripción |
|---|---|
| 🧠 **Chatbot Olivia + Gemini API** | Conversación abierta sobre cualquier síntoma, lesión o duda dermatológica con la Dra. Olivia (Google Gemini `gemini-flash-lite-latest` + fallback empático) |
| 🎯 **Calibración Diagnóstica Multi-Patología** | Resolución integral de conflictos clínicos: protección de Carcinomas Basocelulares (`bcc`), prioridad clínica en sospecha de Melanoma (`mel`, caso `ISIC_0032258`), y diferenciación precisa de Queratosis Actínica (`akiec`) y Benigna (`bkl`) |
| 🔬 **Análisis Visual CNN Adaptativa** | Clasificación de 7 patologías dermatológicas (Melanoma, BCC, AKIEC, BKL, NV, VASC, DF) con arquitectura convolucional profunda (ResNet-50 / ResNet-18) y criterios morfológicos explicables ABCDE |
| 📋 **Informe PDF Clínico** | Generación y descarga de informe clínico completo con imagen de la lesión, diagnóstico ABCDE y recomendación de derivación |
| 🧠 **Cerebro de Olivia** | Memoria persistente cross-session: Olivia recuerda conversaciones anteriores y las usa para personalizar la interacción |
| 📁 **Panel de Historial** | Drawer lateral (estilo ChatGPT) para explorar, seleccionar y restaurar sesiones de conversación previas |
| 📷 **Cámara / Subida de imagen** | Compatible con cámara web, cámara nativa iOS/Android y subida de archivos desde el dispositivo |
| 🔒 **Aviso ético integrado** | Recordatorio permanente de que Olivia es una IA de apoyo, no un diagnóstico definitivo |

---

## Stack Técnico

| Componente | Tecnología |
|---|---|
| **Backend** | Python 3.11+ · FastAPI · Uvicorn |
| **Visión por Computador** | PyTorch · ResNet-50 / ResNet-18 · OpenCV · NumPy |
| **LLM / Chatbot** | Google Gemini API (`google-genai`) · `gemini-flash-lite-latest` |
| **Informe PDF** | ReportLab |
| **Frontend** | HTML5 · Vanilla CSS · JavaScript (ESM) |
| **Tests** | Pytest · 21 tests (unit + integration, 100% pass) |
| **Variables de entorno** | `python-dotenv` |

---

## Instalación y Ejecución

### Requisitos previos

- Python 3.11 o superior
- pip
- Clave API de Google Gemini (obtener en [Google AI Studio](https://aistudio.google.com/))

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar clave API de Gemini

Crea un archivo `.env` en la raíz del proyecto:

```env
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-flash-lite-latest
```

### 3. Iniciar la aplicación

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.cmd
```

### 4. Acceder a OLIVIA

| Dispositivo | URL |
|---|---|
| Escritorio (Mac/PC) | `http://127.0.0.1:8000/` |
| Móvil / iPad (misma red Wi-Fi) | `http://<IP_DE_TU_MAC>:8000/` |

---

## Parar la aplicación

**macOS / Linux:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.cmd
```

---

## Tests Automatizados

```bash
PYTHONPATH=. venv/bin/pytest -v
```

**Estado actual:** `19/19 tests pasando ✅`

```
tests/integration/test_chat_endpoint.py    ✅✅
tests/integration/test_health_endpoint.py  ✅
tests/unit/test_dataset_service.py         ✅✅✅
tests/unit/test_gemini_service.py          ✅✅✅
tests/unit/test_inference_service.py       ✅✅✅✅✅✅✅✅
tests/unit/test_pdf_service.py             ✅✅
```

---

## Estructura del Proyecto

```text
/
├── app/
│   ├── api/
│   │   └── routes.py          # Endpoints FastAPI: /, /health, /analyze, /chat, /download-report-pdf
│   ├── schemas/
│   │   ├── prediction.py      # AnalysisResponse schema
│   │   └── chat.py            # ChatMessageRequest/Response + brain_memory
│   ├── services/
│   │   ├── gemini_service.py  # Dra. Olivia — Google Gemini API + fallback
│   │   ├── inference_service.py # ResNet-18 + ABCDE + triage clínico
│   │   ├── pdf_service.py     # Generador PDF con ReportLab
│   │   └── dataset_service.py # Gestión del dataset HAM10000
│   └── static/
│       ├── css/styles.css     # UI Dark Sci-Fi, animaciones, drawer
│       └── js/app.js          # Lógica frontend, Cerebro, drawer, chat
├── tests/
│   ├── unit/                  # Tests unitarios por servicio
│   └── integration/           # Tests de integración de endpoints
├── docs/
│   ├── SPECIFICATIONS.md      # Especificaciones funcionales SDD
│   ├── ARCHITECTURE.md        # Decisiones técnicas y arquitectura
│   ├── DESIGN.md              # Sistema de diseño visual
│   └── diario_codigo.md       # Diario de desarrollo día a día
├── models/                    # Pesos ResNet-18 entrenada (no en Git)
├── .env                       # Clave API Gemini (no en Git)
├── requirements.txt
├── CHANGELOG.md
├── task.md                    # Estado de tareas SDD
└── memory.md                  # ADRs y decisiones de arquitectura
```

---

## Benchmark ResNet-18 (HAM10000 Test Set — 1.494 imágenes)

| Métrica | Valor |
|---|---|
| Accuracy global | **74.03%** |
| Macro F1 | **0.6081** |
| Sensibilidad en malignos | **78.62%** |
| Precisión en benignos | **93.42%** |

---

## Documentación del Proyecto (SDD)

| Documento | Propósito |
|---|---|
| [`docs/SPECIFICATIONS.md`](docs/SPECIFICATIONS.md) | Especificaciones funcionales y criterios de aceptación |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stack técnico y decisiones de arquitectura |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Sistema de diseño visual y tokens |
| [`docs/diario_codigo.md`](docs/diario_codigo.md) | Diario de desarrollo técnico (11 días) |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones |
| [`task.md`](task.md) | Estado actual de tareas SDD |
| [`memory.md`](memory.md) | ADRs, lecciones aprendidas, contexto activo |
