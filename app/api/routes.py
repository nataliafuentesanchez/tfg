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
        <link href=\"https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap\" rel=\"stylesheet\" />
        <link rel=\"stylesheet\" href=\"/static/css/styles.css\" />
      </head>
      <body>
        <div class=\"bg-orb orb-a\"></div>
        <div class=\"bg-orb orb-b\"></div>
        <main class=\"layout\">
          <section class=\"hero\">
            <p class=\"kicker\">TFG Ingenieria de la Salud</p>
            <h1>Analisis dermatologico asistido por IA</h1>
            <p class=\"subtitle\">
              Subida de imagen, evaluacion automatica de riesgo y recomendacion clinica orientativa
              en una sola vista preparada para demo.
            </p>
            <div class=\"tag-row\">
              <span class=\"tag\">FastAPI</span>
              <span class=\"tag\">Computer Vision</span>
              <span class=\"tag\">Triage de riesgo</span>
            </div>
          </section>

          <section class=\"panel\">
            <div class=\"upload-header\">
              <h2>Analizar imagen</h2>
              <p>Selecciona una imagen dermatologica y ejecuta el analisis.</p>
            </div>

            <label class=\"file-drop\" for=\"img\">
              <input id=\"img\" type=\"file\" accept=\"image/*\" />
              <span id=\"fileName\">Arrastra o selecciona una imagen</span>
            </label>

            <button id=\"analyzeButton\" class=\"analyze-btn\" type=\"button\">Analizar ahora</button>

            <article id=\"report\" class=\"report\">
              Informe legible: pendiente de analisis.
            </article>

            <section class=\"json-block\">
              <header>
                <h3>Salida JSON tecnica</h3>
                <span class=\"pill\">machine-readable</span>
              </header>
              <pre id=\"result\">Esperando imagen...</pre>
            </section>

            <p class=\"disclaimer\">
              Aviso: esta herramienta es de apoyo y no reemplaza el diagnostico medico profesional.
            </p>
          </section>
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
