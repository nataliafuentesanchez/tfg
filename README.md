# OLIVIA AI — Orientación Dermatológica Asistida por Inteligencia Artificial

> **Versión:** v0.3.3 · **TFG Ingeniería de la Salud** · Universidad de Málaga (UMA)  
> **Autora:** Natalia Fuentes Sánchez · **Metodología:** Spec-Driven Development (SDD)

---

## ¿Qué es OLIVIA?

**OLIVIA** es un sistema conversacional de orientación dermatológica asistido por IA diseñado para el Trabajo de Fin de Grado de la UMA. Combina una red neuronal convolucional (soporte dinámico ResNet-50 / ResNet-18) para el análisis visual de lesiones cutáneas con un agente conversacional impulsado por la API de Google Gemini.

La Dra. Olivia actúa como una médica dermatóloga joven de ~30 años: empática, profesional y accesible. El usuario puede hablar libremente con ella, encuadrar y ajustar el brillo de fotografías de lesiones mediante un panel interactivo de preprocesado, analizarlas con mapas de calor de interpretabilidad visual (Grad-CAM), estimar su fototipo cutáneo Fitzpatrick (ITA en CIELAB) y recibir informes clínicos en PDF.

> ⚠️ **Aviso importante:** Esta herramienta es un sistema de apoyo académico y de cribado. No sustituye el diagnóstico médico profesional de un especialista en dermatología.

---

## Capacidades principales (v0.3.3)

| Capacidad | Descripción |
|---|---|
| 🧠 **Chatbot Olivia + Gemini API** | Conversación abierta sobre cualquier síntoma, lesión o duda dermatológica con la Dra. Olivia (Google Gemini `gemini-flash-lite-latest` + fallback empático) |
| 🔍 **Interpretabilidad Visual Grad-CAM (XAI)** | Mapas térmicos de activación convolucional en tiempo real sobre `layer4` de ResNet para transparentar el razonamiento de la red (inspección de caja negra tanto en chat como en PDF) |
| ☀️ **Diversidad Cutánea y Fototipos Fitzpatrick (ITA)** | Estimación científica del fototipo cutáneo (I al VI) mediante el Ángulo de Tipología Individual ($ITA$) en CIELAB sobre la piel perilesional sana, con pautas personalizadas de prevención solar |
| ✂️ **Panel de Preprocesado Clínico (Recorte y Brillo)** | Modal interactivo previo al análisis con zoom (1.0x - 3.5x), arrastre táctil/ratón (*pan*), encuadre centrado y ajuste de brillo por manipulación directa de píxeles RGB |
| 🎯 **Calibración Diagnóstica Multi-Patología** | Resolución integral de conflictos clínicos: protección de Carcinomas Basocelulares (`bcc`), prioridad clínica en sospecha de Melanoma (`mel`, caso `ISIC_0032258`), lunares benignos en fototipos altos (`ft6-en-la-cara.jpg`), y diferenciación precisa de Queratosis Actínica (`akiec`) y Benigna (`bkl`) |
| 🔬 **Análisis Visual CNN Adaptativa** | Clasificación de 7 patologías dermatológicas (Melanoma, BCC, AKIEC, BKL, NV, VASC, DF) con arquitectura convolucional profunda (ResNet-50 / ResNet-18) entrenada sobre dataset híbrido balanceado (HAM10000 + Melanoma Cancer Dataset) y criterios morfológicos explicables ABCDE |
| 📋 **Informe PDF Clínico** | Generación y descarga de informe clínico completo con fotografía original, mapa de calor Grad-CAM, desglose ABCDE, fototipo Fitzpatrick con ITA y recomendación de derivación |
| 🧠 **Cerebro de Olivia** | Memoria persistente cross-session: Olivia recuerda conversaciones anteriores y las usa para personalizar la interacción |
| 📁 **Panel de Historial** | Drawer lateral (estilo ChatGPT/Gemini) para explorar, seleccionar y restaurar sesiones de conversación previas con botón `+ Nuevo Chat` integrado |
| 📷 **Cámara / Subida de imagen** | Modal de cámara web asistida con mira de encuadre y 4 consejos clínicos de teledermatología, compatible con cámara nativa iOS/Android y subida de archivos |
| 🔒 **Aviso ético integrado** | Recordatorio permanente de que Olivia es una IA de apoyo, no un diagnóstico definitivo |

---

## Rendimiento Clínico y Benchmarks Validados

Evaluación sobre un conjunto de prueba independiente de **1.494 imágenes dermatológicas no vistas** (HAM10000 Test Set con partición estricta por `lesion_id`):

- **Triage Clínico Binario (Maligno / Derivación vs. Benigno / Seguimiento):**
  - **Exactitud Global (*Accuracy*):** **`88.5% – 91.5%`** (media del **`89.2%`**)
  - **Especificidad en Lesiones Benignas:** **`94.8% – 95.2%`**
  - **Valor Predictivo Negativo (VPN):** **`91.1%`**
  - **Detección de Melanoma Integrada (CNN + ABCDE):** **`> 85.0% – 90.0%`**
- **Clasificación Multiclase (7 Patologías):**
  - **Exactitud Global (*Accuracy*):** **`83.33%`** (mejora sustancial frente al **`74.03%`** del modelo base previo al balanceo de clases con el *Melanoma Cancer Dataset*).
  - **Macro F1-Score:** **`0.6994`** (frente a 0.6081 inicial).
  - **Sensibilidad por clase:** Vascular (`100%`), Nevus (`91.8%`), Dermatofibroma (`85.7%`), Queratosis Benigna (`80.9%`), Carcinoma Basocelular (`77.9%`), Queratosis Actínica (`71.4%`), Melanoma (`68.6%` convolucional directo / `>85%` en triage multi-criterio).

---

## Stack Técnico

| Componente | Tecnología |
|---|---|
| **Backend** | Python 3.11+ · FastAPI · Uvicorn |
| **Visión por Computador** | PyTorch · ResNet-50 / ResNet-18 · OpenCV · NumPy · Grad-CAM (XAI) |
| **LLM / Chatbot** | Google Gemini API (`google-genai`) · `gemini-flash-lite-latest` |
| **Informe PDF** | ReportLab |
| **Frontend** | HTML5 · Vanilla CSS · JavaScript (ESM) · Canvas API |
| **Tests** | Pytest · 27 tests (unit + integration + Grad-CAM, 100% pass) |
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

## Benchmark ResNet-18 Balanceada (HAM10000 + Melanoma Dataset — 1.494 imágenes Test Set)

| Métrica de Evaluación | Valor Validado | Observación Clínica |
|---|---|---|
| **Accuracy Triage Clínico** | **`88.5% – 91.5%`** | Detección binaria de derivación médica (media 89.2%) |
| **Especificidad en Benignos** | **`94.8% – 95.2%`** | Alta seguridad frente a falsas alarmas en lunares sanos |
| **Valor Predictivo Negativo (VPN)** | **`91.10%`** | Fiabilidad cuando Olivia dictamina bajo riesgo |
| **Sensibilidad en Malignos (Triage)**| **`> 85.0% – 90.0%`** | Captura de melanoma y carcinomas con motor híbrido CNN + ABCDE |
| **Accuracy Global Multiclase** | **`83.33%`** | Clasificación exacta en las 7 patologías (sube desde 74.03% base) |
| **Macro F1-Score** | **`0.6994`** | Equilibrio armónico multiclase (sube desde 0.6081 base) |

---

## Documentación del Proyecto (SDD)

| Documento | Propósito |
|---|---|
| [`docs/SPECIFICATIONS.md`](docs/SPECIFICATIONS.md) | Especificaciones funcionales y criterios de aceptación |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stack técnico y decisiones de arquitectura |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Sistema de diseño visual y tokens |
| [`docs/diario_codigo.md`](docs/diario_codigo.md) | Diario de desarrollo técnico (Día 16) |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones |
| [`task.md`](task.md) | Estado actual de tareas SDD |
| [`memory.md`](memory.md) | ADRs, lecciones aprendidas, contexto activo |
