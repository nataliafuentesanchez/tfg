# Memory - AnalisisImagenes

## Contexto activo

- Proyecto de TFG orientado al analisis dermatologico asistido por IA.
- Objetivo v1: demo web funcional con FastAPI para clasificacion orientativa de riesgo.
- Enfoque actual: imagenes dermatologicas convencionales (RGB), no termografia en v1.

## Decisiones tecnicas

- Arquitectura en dos capas: API web + servicio de inferencia.
- Respuesta dual: informe legible para usuario (`user_report`) y JSON tecnico.
- Umbral de derivacion urgente inicial: `risk_score >= 0.80`.
- Sin base de datos en v1: salida en memoria para simplificar entrega.
- La fase actual es de calibracion con datos reales, no de entrenamiento final: se ajustan features de lesion, fondo, asimetria, borde e histograma rojo antes de pasar a un modelo supervisado.
- La aplicacion ya ha sido validada en navegador y backend; el flujo `frontend -> FastAPI -> servicio -> respuesta` funciona correctamente.

## Riesgos conocidos

- Modelo actual es baseline heuristico, no modelo clinicamente validado.
- Posible desbalance de clases en datasets dermatologicos publicos.
- Riesgo de sobreinterpretacion del resultado por parte del usuario final.
- En esta etapa persiste el problema de falsos positivos al separar lesion/fondo si la mascara no es robusta.

## Lecciones Aprendidas

- La calidad real del algoritmo se decide con datos autenticos, no con una sola prueba visual.
- La mejora relevante se obtuvo al incorporar features morfologicas y de color, no solo por el nivel absoluto de rojo.
- El siguiente salto importante sera la fase supervisada, pero solo despues de estabilizar la calibracion heuristica.

## Guardrails

- Incluir siempre disclaimer de no diagnostico medico.
- Priorizar sensibilidad de casos de riesgo en siguientes iteraciones.
- No almacenar datos personales ni imagenes sensibles en repositorio.
