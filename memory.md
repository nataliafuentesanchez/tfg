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
