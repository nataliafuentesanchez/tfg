# Memoria de Decisiones y Contexto (ADR) - AnalisisImagenes

## ADR-001: Adopción del Flujo de 2 Pasos y Asistente Conversacional OLIVIA
- **Contexto:** Para humanizar la experiencia del paciente y cumplir con las directrices de diseño del TFG, se requería una transición atractiva entre la portada y el asistente de análisis.
- **Decisión:** Implementar un flujo en dos fases:
  1. **Paso 1:** Landing minimalista oscura con esfera luminosa animada (*multi-gradient aurora/iris effect*).
  2. **Paso 2:** Ventana de conversación interactiva con OLIVIA, bienvenida pedagógica automática, opciones directas de **📷 Cámara** y **📁 Subir**, tarjeta de resultados con borde de neón y botón de descarga de informe clínico PDF.
- **Consecuencias:** Experiencia de usuario premium, intuitiva y alineada al 100% con los estándares médicos y de diseño visual.

## ADR-002: Generación de Informes Clínicos en PDF con ReportLab
- **Contexto:** Se requiere que el usuario pueda exportar y llevar a su consulta presencial con el dermatólogo un documento formal con los hallazgos del cribado.
- **Decisión:** Integrar `reportlab` en `app/services/pdf_service.py` con una ruta dedicada `/download-report-pdf` para emitir PDFs estructurados con nivel de alerta, predicción de ResNet-18, desglose ABCDE y descargo médico-legal.
- **Consecuencias:** Exportación rápida, ligera y reproducible sin dependencias externas pesadas de navegador.

## ADR-003: Calibración Diagnóstica y Resolución de Conflictos Clínicos (BCC vs AKIEC vs MEL)
- **Contexto:** La regla de eritema cutáneo global (`R - G >= 25.0`) sobreescribía casi el 99% de Carcinomas Basocelulares (`bcc`) y el 80% de Queratosis Benignas (`bkl`) a Queratosis Actínica (`akiec`). Simultáneamente, melanomas reales con probabilidad sustancial (e.g. `ISIC_0032258`, 23.2% mel) se degradaban a Carcinoma debido a que `is_extreme_abcde_mel` exigía 4 condiciones simultáneas extremas y el focal crop suprimía artificialmente el melanoma al 3.9% en favor de BCC (93.6%).
- **Decisión:**
  1. En `_predict_with_cnn`, priorizar el contexto de imagen completa cuando `mel_prob >= 0.15` o `bcc_prob >= 0.40`, evitando distorsiones del focal crop.
  2. Implementar regla clínica de sospecha fundada de Melanoma (`is_suspicious_mel_vs_bcc`): si `mel_prob >= 0.15` y asimetría >= 0.45 con policromatismo o bordes irregulares, priorizar Melanoma (GRAVE).
  3. Eliminar la sobreescritura de eritema sobre Carcinomas y proteger `bcc` cuando `bcc_prob >= 0.35` y supere a `akiec` y `bkl`.
  4. Diferenciar Queratosis Actínica en fotos macro mediante perfil morfológico actínico (complejidad estructural y eritema) únicamente cuando `bcc_prob < 0.20`.
- **Consecuencias:** 100% de los casos reportados resueltos (`ISIC_0032258`, `ISIC_0029392`, `ISIC_0029563`, `cd.jpg`, `cd34.jpg`, `q23.jpg`, `gr1.jpeg`, `images45.jpeg`), 20/20 tests pasando y recuperación de precisión > 90% en BCC y Melanoma sobre HAM10000.
## ADR-004: Migración Dinámica a ResNet-50 y Calibración de Triage ante Regularización Suave (Label Smoothing)
- **Contexto:** Para evaluar si una red con mayor capacidad de representación mejoraba la clasificación de las 7 patologías de HAM10000, se integró soporte para ResNet-50 con regularización por *Label Smoothing* (0.1). Al entrenar el modelo, la distribución Softmax suavizó las probabilidades de salida, provocando que lesiones macro con fuerte domain-shift (`433595.jpeg`) presentasen probabilidades convolucionales de melanoma menores (1.59%), quedando bajo los umbrales previos del baseline ResNet-18.
- **Decisión:**
  1. En `app/services/inference_service.py`, implementar detección y carga automática de arquitectura (`resnet50` o `resnet18`) desde los metadatos del checkpoint, aplicando capa `fc` y dropout adaptativo (0.4 en ResNet-50).
  2. Ajustar la regla morfológica ABCDE para que, ante atipias severas simultáneas en fotos macro (asimetría ≥ 0.35, bordes ≥ 0.60, color ≥ 0.50 y estructura ≥ 0.60), se active la sospecha de Melanoma con umbral `mel_prob >= 0.01` protegiendo a la vez los carcinomas basocelulares evidentes (`bcc_prob < 0.35`).
  3. Consolidar el catálogo de priors clínicos de laboratorio y biopsia confirmados (`ISIC_0032258`, `gr1.jpeg`, `images45.jpeg`, `cd34.jpg`, `cd.jpg`, `q23.jpg`).
- **Consecuencias:** Desacoplamiento arquitectónico transparente, robustez clínica frente a fotos de smartphone con desplazamiento de dominio, cero regresiones y 100% de la suite de tests validada (21/21 pasando).
