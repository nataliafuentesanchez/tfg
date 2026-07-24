# 🏗 Arquitectura Técnica: AnalisisImagenes

> **Fase:** `/plan` (Planificación Técnica)
> **Estado:** Borrador inicial
> **Última Revisión:** 2026-07-24

---

## 🛠 Stack Tecnológico

| Capa | Tecnología | Justificación |
| --- | --- | --- |
| **Lenguaje** | Python 3.11+ | Ecosistema maduro para IA medica e integracion rapida |
| **Framework principal** | FastAPI + Uvicorn | API web ligera y rapida para demo funcional |
| **Pipeline CV/IA** | OpenCV + PyTorch | Preprocesado de imagen + inferencia de clasificacion |
| **Persistencia** | Sin BD en v1 (archivos CSV/JSON) | Reducir complejidad para entrega inicial |
| **Testing** | Pytest | Pruebas unitarias e integracion de endpoints |
| **CI/CD** | No aplicable en v1 | Fuera de alcance para demo en 30 minutos |

---

## 📂 Estructura de Directorios

```text
/
├── app/
│   ├── main.py           # Entrada FastAPI
│   ├── api/              # Endpoints web
│   ├── services/         # Logica de analisis e inferencia
│   ├── ml/               # Carga de modelo y utilidades IA
│   └── schemas/          # Modelos de peticion/respuesta
├── tests/
│   ├── unit/
│   └── integration/
├── data/
│   ├── samples/          # Imagenes de prueba local
│   └── outputs/          # Resultados de inferencia
├── docs/                # Documentación del proyecto (este directorio)
└── requirements.txt      # Dependencias Python
```

> Adapta esta estructura al stack elegido. Si es un proyecto pequeño, una sola carpeta `src/` plana es suficiente.

---

## 🔑 Decisiones Técnicas Clave

### Seguridad

- **Autenticación:** No incluida en v1 de demo.
- **Autorización:** No incluida en v1 de demo.
- **Datos sensibles:** No almacenar datos personales; usar datasets anonimizados y rutas locales fuera de control de versiones.

### Estilo de Código

- **Paradigma:** Modular, funciones puras para preprocesado e inferencia.
- **Convenciones:** Ver repo de referencia en `MASTER_PROMPT.md`
- **Complejidad máxima por función:** Preferencia <= 30 lineas por funcion en v1.

### Gestión de Estado

- Estado transitorio en memoria durante inferencia y export de resultados a archivo.

---

## 🔗 Integraciones Externas

| Servicio | Propósito | Notas / Límites |
| --- | --- | --- |
| ISIC/HAM10000/PAD-UFES-20 | Dataset de entrenamiento/evaluacion | Revisar licencias antes de publicacion |

---

## ⚠️ Restricciones y Riesgos Técnicos

- **Restricción:** Demo funcional objetivo en 30 minutos.
- **Riesgo:** Escasez de datos termograficos dermatologicos publicos para v1.
  - **Mitigación:** Iniciar con imagenes RGB/dermatoscopicas y planificar fase 2 multimodal.
- **Riesgo:** Falsos negativos en casos peligrosos.
  - **Mitigación:** Umbral de derivacion urgente conservador (>= 0.80) y mensaje explicito de apoyo, no diagnostico.

---

## 🤖 Agent Harness (Arnés del Agente)

> Rellena esta sección para configurar la infraestructura, el contexto y las herramientas que rodean al agente de IA para que trabaje de forma segura y autónoma.

### 1. Gestión de Contexto (Context Engineering)
- **Contexto Estático:** `project.config.md`, `docs/SPECIFICATIONS.md`, `docs/ARCHITECTURE.md`, `memory.md`, `task.md`.
- **Contexto Dinámico / Skills:** No definido aun; fuera de alcance de v1.

### 2. Herramientas y MCP (Model Context Protocol)
- **Servidores MCP Requeridos:** Ninguno obligatorio en v1.
- **Propósito:** No aplica para demo inicial.
- **Configuración de Herramientas:** Ver `.claude/settings.json`, `.windsurfrules` o equivalentes.

### 3. Entorno de Ejecución (Sandboxing)
- **Aislamiento:** Entorno virtual local Python (`venv/`).
- **Límites de Ejecución:** Iteraciones cortas para cumplir demo rapida.

### 4. Guardrails Deterministas de Seguridad
- **Filtros de Código:** Revision manual de secretos y dependencias en esta fase.
- **Políticas de Commit/Push:** No versionar datos clinicos ni rutas sensibles.

### 5. Interfaz Externa para Agentes (Agent Readiness)
*Define la arquitectura y métodos que permiten a agentes externos descubrir y consumir los servicios del sitio:*
- **Autodescubrimiento**: No aplica en v1 (Agent Readiness desactivado).
- **Protocolos y Tarjetas**: No aplica en v1.
- **Formato del Contenido**: No aplica en v1.

---

**Instrucción para la IA:** Respeta las decisiones y configuraciones del arnés documentadas aquí. Si necesitas desviarte por un motivo técnico o sugerir una nueva herramienta MCP/Skill para el proyecto, regístralo como "Decisión Técnica" en `memory.md` y obtén la aprobación del desarrollador.
