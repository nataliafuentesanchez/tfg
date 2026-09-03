# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.schemas.prediction import AnalysisResponse
from app.services.inference_service import analyze_image

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!DOCTYPE html>
    <html lang="es">
      <head>
        <title>OLIVIA - Analisis Dermatologico</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="/static/css/styles.css" />
      </head>
      <body>
        <main class="landing">
          <div class="orb"></div>

          <h1 class="brand">OLIVIA</h1>
          <div class="brand-line"></div>

          <p class="lead">Si cuidas tu piel, iluminará tu futuro.</p>
          <p class="sublead">Selecciona una imagen dermatológica para comenzar el análisis con IA (ResNet-18).</p>

          <div class="options">
            <button class="option-btn upload-trigger" type="button" id="uploadBtn">
              <span class="dot"></span>
              <span>📁 Seleccionar imagen dermatológica</span>
            </button>
          </div>

          <input id="img" type="file" accept="image/*" hidden />

          <!-- Previsualizacion de Imagen Seleccionada -->
          <div class="preview-card" id="previewCard" style="display: none;">
            <div class="mini-label">Imagen para análisis</div>
            <div class="preview-img-wrapper">
              <img id="previewImg" src="" alt="Previsualización de lesión" />
            </div>
          </div>

          <div class="result-panel" id="resultPanel" style="display: none;">
            <div class="mini-label">Resultado del análisis de la Red Neuronal</div>
            <p id="analysisText">Esperando imagen...</p>
          </div>

          <div class="json-box" id="jsonBox" style="display: none;">
            <div class="mini-label">Detalles técnicos del modelo y Criterios ABCDE (JSON)</div>
            <pre id="result">Esperando análisis...</pre>
          </div>

          <button id="analyzeButton" class="analyze-btn" type="button">Analizar ahora</button>
        </main>

        <script src="/static/js/app.js"></script>
      </body>
    </html>
    """


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)) -> AnalysisResponse:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="No se ha recibido contenido de imagen.")

    try:
        return analyze_image(content, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
