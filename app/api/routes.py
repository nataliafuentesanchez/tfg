# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from fastapi import APIRouter, File, HTTPException, UploadFile, Response
from fastapi.responses import HTMLResponse

from app.schemas.prediction import AnalysisResponse
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.inference_service import analyze_image
from app.services.pdf_service import generate_clinical_pdf
from app.services.gemini_service import generate_olivia_response

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
    <link rel="stylesheet" href="/static/css/styles.css?v=2.1" />
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
            <div class="chat-header-left" id="openHistoryDrawerBtn" title="Ver Cerebro e Historial de Olivia">
              <div class="header-avatar">
                <div class="mini-orb"></div>
              </div>
              <div class="header-meta">
                <span class="bot-name">OLIVIA AI</span>
                <span class="brain-badge">🧠 Cerebro & Historial</span>
              </div>
            </div>
            <div class="chat-header-right">
              <span class="status-pill"><span class="online-dot"></span> En línea</span>
              <button class="new-chat-btn" id="newChatBtn" title="Abrir nuevo chat">+ Nuevo Chat</button>
              <button class="back-home-btn" id="backToLandingBtn" title="Volver al inicio">⟵ Inicio</button>
            </div>
          </header>

          <!-- Chat Messages Scroll Area -->
          <div class="chat-messages-area" id="chatMessagesArea">
            
            <!-- Mensaje de bienvenida de Olivia -->
            <div class="chat-msg-row bot-row">
              <div class="msg-avatar"><div class="mini-orb"></div></div>
              <div class="msg-bubble welcome-bubble">
                <p>✨ <strong>¡Nuevo chat iniciado!</strong> Soy la <strong>Dra. Olivia</strong>, tu médica asistencial de orientación dermatológica.</p>
                <p style="margin-top: 6px;">Puedes preguntarme cualquier duda sobre tu piel, síntomas o subir una fotografía para analizarla:</p>
                <ul class="guide-options-list" style="margin-top: 6px;">
                  <li>• Escribe tus preguntas o dudas médicas directamente abajo.</li>
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
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span style="font-size: 0.85rem; color: #94a3b8;">La Dra. Olivia está escribiendo...</span>
              </div>
            </div>

          </div>

          <!-- Chat Input Bar -->
          <footer class="chat-input-bar">
            <div class="input-actions-left">
              <button class="action-btn btn-upload" id="uploadActionBtn" title="Subir imagen" type="button">
                <span>📁 Subir</span>
              </button>
              <button class="action-btn btn-camera" id="cameraActionBtn" title="Usar Cámara" type="button">
                <span>📷 Cámara</span>
              </button>
              <input type="file" id="fileInputHidden" accept="image/*" style="display: none;" />
            </div>

            <form class="chat-input-form" id="chatForm">
              <input 
                type="text" 
                id="chatTextInput" 
                class="chat-text-input" 
                placeholder="Escribe tu consulta médica o habla con Olivia..." 
                autocomplete="off" 
              />
              <button class="send-btn" id="sendTextMsgBtn" type="submit" title="Enviar mensaje">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </form>
          </footer>

        </div>
      </section>

    </div>

    <!-- Modal de Cámara Web / Móvil -->
    <div class="camera-modal" id="cameraModal" style="display: none;">
      <div class="camera-modal-backdrop" id="closeCameraBackdrop"></div>
      <div class="camera-modal-content">
        <div class="camera-modal-header">
          <h3>📷 Cámara en directo</h3>
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
    <!-- ================= PANEL LATERAL (CEREBRO / HISTORIAL DE CHATS) ================= -->
    <div class="history-drawer" id="historyDrawer" style="display: none;">
      <div class="history-drawer-backdrop" id="closeDrawerBackdrop"></div>
      <div class="history-drawer-content">
        <div class="drawer-header">
          <div class="drawer-title-row">
            <div class="mini-orb"></div>
            <div>
              <h3 class="drawer-title">🧠 Cerebro de Olivia</h3>
              <span class="drawer-subtitle">Recopilación de conversaciones y análisis de sesiones previas</span>
            </div>
          </div>
          <button class="close-modal-btn" id="closeDrawerBtn">&times;</button>
        </div>
        
        <div class="drawer-actions">
          <button class="action-btn btn-new-chat-drawer" id="drawerNewChatBtn" type="button">+ Nuevo Chat</button>
          <button class="action-btn btn-home-drawer" id="drawerHomeBtn" type="button">⟵ Inicio</button>
        </div>

        <div class="drawer-section-label">📋 SESIONES Y ANALISIS GUARDADOS:</div>
        <div class="drawer-history-list" id="drawerHistoryList">
          <!-- Sesiones de chat cargadas dinámicamente -->
        </div>
      </div>
    </div>

    <script src="/static/js/app.js?v=2.2"></script>
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


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_olivia(request: ChatMessageRequest) -> ChatMessageResponse:
    try:
        history_list = [item.model_dump() for item in request.history] if request.history else []
        reply_text, chips, status = generate_olivia_response(
            user_message=request.message,
            history=history_list,
            analysis_context=request.analysis_context,
        )
        return ChatMessageResponse(
            reply=reply_text,
            suggested_questions=chips,
            status=status
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en el asistente conversacional: {exc}") from exc
