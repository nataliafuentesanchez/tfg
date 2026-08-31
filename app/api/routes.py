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
    return """
    <html lang=\"es\">
      <head>
        <title>AnalisisImagenes</title>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
        <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
        <link href=\"https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Cormorant+Garamond:wght@400;500;600;700&display=swap\" rel=\"stylesheet\" />
        <link rel=\"stylesheet\" href=\"/static/css/styles.css\" />
      </head>
      <body>
        <main class=\"landing\">
          <div class=\"orb\"></div>

          <h1 class=\"brand\">OLIVIA</h1>
          <div class=\"brand-line\"></div>

          <p class=\"lead\">Si cuidas tu piel, iluminará tu futuro.</p>
          <p class=\"sublead\">Selecciona una opción para comenzar tu análisis.</p>

          <div class=\"options\">
            <button class=\"option-btn\" type=\"button\" id=\"cameraBtn\">
              <span class=\"dot\"></span>
              <span>Usar cámara del móvil</span>
            </button>

            <button class=\"option-btn upload-trigger\" type=\"button\" id=\"uploadBtn\">
              <span class=\"dot\"></span>
              <span>Subir archivo de imagen</span>
            </button>
          </div>

          <input id=\"img\" type=\"file\" accept=\"image/*\" hidden />

          <div class=\"result-panel\" id=\"resultPanel\" hidden>
            <div class=\"mini-label\">Resultado del análisis</div>
            <p id=\"analysisText\">No hay análisis todavía.</p>
          </div>

          <div class=\"json-box\" id=\"jsonBox\" hidden>
            <pre id=\"result\">Esperando imagen...</pre>
          </div>

          <button id=\"analyzeButton\" class=\"analyze-btn\" type=\"button\">Analizar ahora</button>
        </main>

        <script src=\"/static/js/app.js\"></script>
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
