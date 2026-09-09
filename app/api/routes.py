# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from fastapi import APIRouter, File, HTTPException, UploadFile, Response
from fastapi.responses import HTMLResponse

from app.schemas.prediction import AnalysisResponse
from app.services.inference_service import analyze_image
from app.services.pdf_service import generate_clinical_pdf

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!DOCTYPE html>
<html lang="es">
  <head>
    <title>OLIVIA AI · Orientación Dermatológica</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;1,400&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/static/css/styles.css" />
  </head>
  <body>
    <div class="app-viewport">
      
      <!-- ================= PASO 1: LANDING CON ESFERA ================= -->
      <section class="step-container step-landing active" id="step1Landing">
        <div class="landing-card">
          <h1 class="brand-title">OLIVIA</h1>
          <p class="brand-tagline">Si cuidas tu piel, iluminará tu futuro.</p>

          <div class="orb-wrapper" id="sphereTrigger" title="Pulsa para comenzar la conversación">
            <div class="orb-glow"></div>
            <div class="orb-core">
              <div class="orb-swirl swirl-1"></div>
              <div class="orb-swirl swirl-2"></div>
              <div class="orb-swirl swirl-3"></div>
            </div>
          </div>

          <button class="start-pill-btn" id="startConversationBtn" type="button">
            <span>Presiona la esfera para comenzar tu conversación con Olivia</span>
          </button>

          <div class="legal-footnote">
            Herramienta de cribado asistida por IA · No sustituye la valoración médica
          </div>
        </div>
      </section>

      <!-- ================= PASO 2: CONVERSACIÓN, ANÁLISIS Y PDF ================= -->
      <section class="step-container step-chat" id="step2Chat">
        <div class="chat-window">
          
          <!-- Chat Header -->
          <header class="chat-header">
            <div class="chat-header-left">
              <div class="header-avatar">
                <div class="mini-orb"></div>
              </div>
              <div class="header-meta">
                <span class="bot-name">OLIVIA AI</span>
              </div>
            </div>
            <div class="chat-header-right">
              <span class="status-pill"><span class="online-dot"></span> En línea</span>
              <button class="back-home-btn" id="backToLandingBtn" title="Volver al inicio">⟵ Inicio</button>
            </div>
          </header>

          <!-- Chat Messages Scroll Area -->
          <div class="chat-messages-area" id="chatMessagesArea">
            
            <!-- Mensaje de bienvenida de Olivia -->
            <div class="chat-msg-row bot-row">
              <div class="msg-avatar"><div class="mini-orb"></div></div>
              <div class="msg-bubble welcome-bubble">
                <p>¡Hola! Soy OLIVIA. ¿Cómo deseas realizar el análisis de tu piel?</p>
                <ul class="guide-options-list">
                  <li>• Pulsa <strong>📷 Cámara</strong> para tomar una foto en directo.</li>
                  <li>• Pulsa <strong>📁 Subir</strong> para seleccionar una imagen de tu dispositivo.</li>
                </ul>
              </div>
            </div>

            <!-- Contenedor dinámico para respuestas y resultados -->
            <div id="dynamicChatEntries"></div>

            <!-- Loader animado mientras analiza -->
            <div class="chat-msg-row bot-row" id="typingLoader" style="display: none;">
              <div class="msg-avatar"><div class="mini-orb"></div></div>
              <div class="msg-bubble loading-bubble">
                <div class="typing-dots">
                  <span></span><span></span><span></span>
                </div>
                <span class="loading-label">Analizando patrones de la lesión con ResNet-18...</span>
              </div>
            </div>

          </div>

          <!-- Barra inferior de entrada y botones -->
          <footer class="chat-footer-bar">
            <div class="input-container-fake">
              <input type="text" class="chat-input-field" id="chatTextInput" placeholder="Escribe o pulsa un botón..." readonly />
            </div>
            <div class="footer-action-buttons">
              <button class="action-btn btn-camera" id="cameraActionBtn" type="button">
                <span class="btn-icon">📷</span>
                <span>Cámara</span>
              </button>
              <button class="action-btn btn-upload" id="uploadActionBtn" type="button">
                <span class="btn-icon">📁</span>
                <span>Subir</span>
              </button>
            </div>
          </footer>

        </div>
      </section>

    </div>

    <!-- Hidden File Input -->
    <input id="fileInputHidden" type="file" accept="image/*" hidden />

    <!-- Modal de Cámara Web -->
    <div class="camera-modal" id="cameraModal" style="display: none;">
      <div class="camera-modal-backdrop" id="closeCameraBackdrop"></div>
      <div class="camera-modal-content">
        <div class="camera-modal-header">
          <h3>📷 Captura en directo con la cámara</h3>
          <button class="close-modal-btn" id="closeCameraBtn">&times;</button>
        </div>
        <div class="video-wrapper">
          <video id="webcamVideo" autoplay playsinline muted></video>
          <canvas id="webcamCanvas" style="display: none;"></canvas>
        </div>
        <div class="camera-modal-actions">
          <button class="action-btn btn-camera" id="snapPhotoBtn" type="button">📸 Tomar Foto y Analizar</button>
        </div>
      </div>
    </div>

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


@router.post("/download-report-pdf")
async def download_report_pdf(analysis: AnalysisResponse) -> Response:
    try:
        pdf_bytes = generate_clinical_pdf(analysis.model_dump())
        filename = f"informe_olivia_{analysis.filename.split('.')[0]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {exc}") from exc
