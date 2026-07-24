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

## Riesgos conocidos

- Modelo actual es baseline heuristico, no modelo clinicamente validado.
- Posible desbalance de clases en datasets dermatologicos publicos.
- Riesgo de sobreinterpretacion del resultado por parte del usuario final.

## Guardrails

- Incluir siempre disclaimer de no diagnostico medico.
- Priorizar sensibilidad de casos de riesgo en siguientes iteraciones.
- No almacenar datos personales ni imagenes sensibles en repositorio.
