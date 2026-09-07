# Memory - AnalisisImagenes

## Contexto activo

- Proyecto de TFG de Ingeniería de la Salud (Universidad de Málaga): OLIVIA (Análisis Dermatológico con IA y XAI).
- Modelo en producción: Red Neuronal Convolucional (ResNet-18) con Transfer Learning y Weighted Loss, entrenada sobre 10.015 imágenes de HAM10000 con split 70/15/15 agrupado por `lesion_id`.
- Triage Clínico (Día 5): Matriz ontológica de 7 patologías (`nv`, `bkl`, `vasc`, `df`, `akiec`, `bcc`, `mel`) con plantilla estandarizada y visor frontend modular por tarjetas.
- Precisión clínica actual: Recall en malignos `78.62%`, VPN `93.42%`, Macro F1 `0.6081`.

## Decisiones tecnicas

- **Inferencia:** ResNet-18 con cabezal de 7 clases (`Linear(512, 7)`) y Dropout(0.3) + Módulo Biométrico ABCDE (IA Explicable - XAI).
- **Triage de Severidad Clínico:**
  - `mel` $\rightarrow$ **ENFERMO / MALIGNO** | **GRAVE** | Derivación urgente inmediata.
  - `bcc` $\rightarrow$ **ENFERMO / MALIGNO** | **MODERADO**.
  - `akiec` $\rightarrow$ **ENFERMO / PREMALIGNO** | **LEVE - MODERADO** (Premaligna, nunca grave).
  - Benignos (`nv`, `bkl`, `vasc`, `df`) $\rightarrow$ **SANO / BENIGNO** | **BAJO RIESGO** con recomendación preventiva.
- **Frontend Modular:** Presentación estructurada en 4 paneles: Cabecera con Badge, Métricas en Grid, Contexto Clínico, Criterios ABCDE y Recomendación/Derivación.

## Lecciones Aprendidas

- El cálculo de riesgo agregado diluía la señal de melanoma si la clase mayoritaria era benigna (`nv`); se resolvió mediante disparo directo por probabilidad de clase individual ($P(\text{mel}) \ge 15\%$).
- Las queratosis actínicas (`akiec`) deben catalogarse como premalignas con alerta leve-moderada para evitar falsas alarmas de malignidad grave.
- Separar la respuesta en bloques visuales e interactivos mejora notablemente la comprensión y la experiencia de usuario frente a párrafos de texto continuo.

## Guardrails

- Disclaimer médico siempre visible en frontend y respuestas JSON.
- Respetar estrictamente la partición por `lesion_id` para evitar fuga de datos (*data leakage*).
- Mantener la reproducibilidad del entorno y tests automáticos passing antes de cada cierre.

