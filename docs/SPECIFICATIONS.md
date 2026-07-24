# 📋 Especificaciones: AnalisisImagenes

> **Fase:** `/spec` (Especificacion)
> **Estado:** Validado para pasar a /plan
> **Ultima Revision:** 2026-07-24

---

## 🎯 1. Contexto y Objetivos
*Basado en la filosofía de "entender el problema antes de proponer la solución".*

- **Problema:** [CONFIRMADO] Se necesita un sistema de apoyo para analizar imagenes medicas dermatologicas que permita detectar patrones compatibles con cancer de piel y priorizar casos de riesgo. La termografia se contempla como expansion futura.
- **Objetivo (Éxito):** [CONFIRMADO] Construir una primera version funcional que clasifique imagenes en sano o enfermo, estime gravedad (bajo, medio, peligro), e incluya recomendacion de derivacion al dermatologo de turno, con resultados trazables para el TFG.

## 👥 2. Usuarios y Escenarios
*Identifica para quién construimos y en qué situaciones usarán el sistema.*

- **Perfil de Usuario:** [CONFIRMADO] Investigadora del TFG (Natalia), tutor/a academico y personal clinico como usuarios secundarios para revisar resultados y priorizar evaluacion dermatologica.
- **Escenarios Clave:**
  - *Escenario A:* [CONFIRMADO] Subir imagen dermatologica (idealmente termografica o multimodal) desde interfaz web y recibir clasificacion de riesgo.
  - *Escenario B:* [CONFIRMADO] Clasificar como sano o enfermo; si es enfermo, asignar nivel de gravedad bajo, medio o peligro y mostrar recomendacion de derivacion.
  - *Escenario C:* [INFERIDO] Registrar evidencia de la prediccion (probabilidades y explicacion basica) para soporte academico del TFG.

## ✨ 3. Funcionalidades Principales (Requisitos)
*El "Qué" del sistema. Estas tareas se trasladarán luego a `task.md`.*

- [ ] **Clasificacion clinica primaria:** [CONFIRMADO] Clasificar cada caso como sano o enfermo.
  - **Criterio de aceptacion:** El sistema devuelve etiqueta primaria y probabilidad asociada para cada imagen.
- [ ] **Estratificacion de gravedad:** [CONFIRMADO] Para casos enfermos, clasificar gravedad en bajo, medio o peligro.
  - **Criterio de aceptacion:** Se devuelve nivel de gravedad con umbrales documentados y justificacion basica.
- [ ] **Subclasificacion benigno/maligno:** [CONFIRMADO] Dentro de casos sospechosos, estimar benignidad/malignidad.
  - **Criterio de aceptacion:** El resultado incluye categoria benigno o maligno con score de confianza.
- [ ] **Recomendacion de derivacion:** [CONFIRMADO] Sugerir derivacion al dermatologo de turno cuando se detecte riesgo clinico.
  - **Criterio de aceptacion:** Si el caso es peligro o maligno probable, el sistema marca prioridad alta de revision dermatologica.
- [ ] **Interfaz web clinica minima:** [CONFIRMADO] Exponer el flujo mediante aplicacion web basada en FastAPI.
  - **Criterio de aceptacion:** El usuario puede cargar imagen, ejecutar analisis y visualizar resultado en navegador.

## 🏗️ 4. Propuesta de Solución Técnica (Resumen)
*Enlace directo con `ARCHITECTURE.md`.*

- **Enfoque:** [CONFIRMADO] Arquitectura en dos capas: backend web con FastAPI + modulo de IA para inferencia dermatologica sobre imagenes.
- **Dependencias Críticas:** [INFERIDO] FastAPI/Uvicorn para API web, OpenCV y/o scikit-image para preprocesado, PyTorch para modelo de vision, pandas para trazabilidad de resultados.
- **Oportunidades de Skills y MCPs**: [INFERIDO] Mantener fuera de alcance inicial; valorar cuando exista pipeline estable.
- **Sistema de Diseño:** [PENDIENTE] Interfaz web funcional y simple; el detalle visual se definira en `docs/DESIGN.md` si se amplian requisitos UX.

### 4.0. Estrategia de Datos para Dermatologia y Termografia
- **Fuente principal recomendada (inicio):** [INFERIDO] ISIC Archive y HAM10000 para bootstrap del clasificador dermatologico RGB.
- **Fuente clinica con metadatos:** [INFERIDO] PAD-UFES-20 como conjunto complementario por incluir variables clinicas y diagnostico.
- **Termografia:** [PENDIENTE CRITICO] Validar disponibilidad de dataset termografico dermatologico publico suficiente. Si no hay volumen adecuado, se propone fase 1 RGB dermatoscopico y fase 2 fusion con termografia.
  - **Decision actual:** [CONFIRMADO] Iniciar con imagen dermatologica convencional (RGB/dermatoscopia) por simplicidad de datos y tiempo.

### 4.1. Agent Readiness Checklist (Proyectos Web)
*Si la configuración de Agent Readiness (Web) está activa, documentar las tareas de descubrimiento para agentes inteligentes:*
- [ ] **No aplica en esta fase:** `Agent Readiness (Web)` esta desactivado en `project.config.md`.

## 🚫 5. Fuera de Alcance (Out of Scope)
*Vital para evitar el "scope creep" (crecimiento descontrolado del proyecto).*

- [ ] [CONFIRMADO] Diagnostico medico definitivo o sustitucion de criterio dermatologico.
- [ ] [INFERIDO] Integracion hospitalaria real (HIS/EHR) en la primera version.
- [ ] [INFERIDO] Automatizacion real de citas con dermatologo en la primera iteracion (solo recomendacion/triage).

## ⚠️ 6. Riesgos y Mitigación
*Anticipar problemas es de ingenieros senior.*

- **Riesgo:** [CONFIRMADO] Escasez de datasets termograficos dermatologicos publicos con etiquetas robustas.
  - **Mitigación:** [INFERIDO] Plan por fases: entrenar base en datasets dermatoscopicos (ISIC/HAM10000/PAD-UFES-20) y anadir termografia al disponer de datos validados.
- **Riesgo:** [INFERIDO] Desbalance de clases (muchos benignos y pocos malignos graves) que degrade sensibilidad en casos peligrosos.
  - **Mitigación:** [INFERIDO] Usar ponderacion de clases, augmentacion y metricas centradas en recall/sensibilidad para casos enfermos.
- **Riesgo de Seguridad y Privacidad (IA/Datos):** [CONFIRMADO] Exposicion de imagenes clinicas y metadatos personales.
  - **Mitigación:** [INFERIDO] Anonimizacion estricta, control de acceso, almacenamiento minimizado y uso de datasets con licencias compatibles.
- **Riesgo Clinico y Regulatorio:** [CONFIRMADO] Sobre-interpretacion del sistema como diagnostico definitivo.
  - **Mitigación:** [CONFIRMADO] Etiquetar la herramienta como apoyo a la decision y exigir revision por dermatologia para casos positivos.

## ❓ 7. Preguntas Abiertas
*Cosas que aún no sabemos o decisiones que dependen del usuario.*

- [x] [CONFIRMADO] Termografia: no es obligatoria en v1; se puede iniciar con imagenes normales.
- [x] [CONFIRMADO] Alcance v1: sin preferencia estricta; se adopta implementacion incremental para reducir riesgo en demo.
- [x] [CONFIRMADO] Umbral inicial de derivacion urgente: probabilidad de riesgo >= 0.80 (ajustable en configuracion).
- [x] [CONFIRMADO] Restricciones de comite etico adicionales: no reportadas en esta fase.
- [x] [CONFIRMADO] Fecha objetivo de demo funcional web: 30 minutos.

## 🧪 8. Criterios de Evaluación y Evals (No Deterministas)
*Define las rúbricas y métricas de calidad para evaluar la salida de componentes no deterministas (IA, prompts, etc.) integrados en la fase /test.*

- [ ] **Metricas de Output:** [CONFIRMADO] Sensibilidad/Recall en clase enfermo, F1 macro por clase, AUC ROC para benigno/maligno, y matriz de confusion por gravedad.
- [ ] **Metricas de Seguridad Clinica:** [INFERIDO] Minimizar falsos negativos en clase peligro como objetivo primario.
- [ ] **Metricas de Trayectoria:** [INFERIDO] Tiempo de respuesta por inferencia web, tasa de errores del endpoint, reproducibilidad de resultados por corrida.

---
**Instrucción para la IA:** No pases a la fase `/plan` hasta que las "Preguntas Abiertas" críticas hayan sido resueltas o tengan un camino de solución definido.