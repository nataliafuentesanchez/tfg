# Sistema de Diseno - AnalisisImagenes

Estado: Implementado en v0.1.0
Ultima revision: 2026-07-24

## Objetivo visual

Transmitir confianza clinica, claridad tecnica y calidad academica para presentacion de TFG.
La interfaz debe ser impactante en demo, pero entendible para perfiles no tecnicos.

## Tokens principales

- Fondo base: `#f5f4ef`
- Fondo secundario: `#e5ecdf`
- Texto principal: `#1f2a2b`
- Texto secundario: `#5f6b6d`
- Superficie tarjeta: `#ffffff`
- Acento principal: `#00695c`
- Acento secundario: `#b75f2a`
- Exito: `#2f7d32`
- Linea suave: `#d8ddd6`
- Fondo de bloque tecnico: `#1d2426`

## Tipografia

- Titulos: `DM Serif Display`
- Texto y UI: `Manrope`

## Componentes clave

- Hero editorial con mensaje de valor del sistema.
- Tarjeta de analisis con:
  - selector de imagen
  - boton principal de accion
  - informe legible de salida
  - panel JSON tecnico
- Etiquetas de tecnologia para contexto de demo.
- Mensaje de disclaimer clinico visible.

## Comportamiento UX

- Feedback inmediato al seleccionar archivo.
- Estado de carga durante analisis (`Analizando...`).
- Salida dual:
  - texto natural para usuario
  - JSON para trazabilidad tecnica

## Responsividad

- Desktop: layout en 2 columnas (hero + panel).
- Mobile: layout en una columna, espaciado reducido.

## Implementacion

- Estilos: `app/static/css/styles.css`
- Interaccion: `app/static/js/app.js`
- Marcado HTML servido por FastAPI en `app/api/routes.py`
