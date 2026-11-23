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
    <link rel="stylesheet" href="/static/css/styles.css?v=4.2" />
  </head>
  <body>
    <div class="app-viewport">
      
      <!-- Fondos de Aurora Ambiental Cósmica -->
      <div class="aurora-ambient aurora-top-left" aria-hidden="true"></div>
      <div class="aurora-ambient aurora-bottom-right" aria-hidden="true"></div>
      
      <!-- ================= PASO 1: LANDING CON ESFERA ================= -->
      <section class="step-container step-landing active" id="step1Landing">
        <div class="landing-card">
          
          <!-- Badge Icon Superior: Cámara / Dermatoscopio -->
          <div class="brand-badge-icon" aria-hidden="true">
            <svg class="bracket-camera-svg" viewBox="0 0 64 64" fill="none">
              <!-- Cuatro esquinas de encuadre -->
              <path d="M16 26V18C16 16.8954 16.8954 16 18 16H26" stroke="#c084fc" stroke-width="2.2" stroke-linecap="round"/>
              <path d="M48 26V18C48 16.8954 47.1046 16 46 16H38" stroke="#c084fc" stroke-width="2.2" stroke-linecap="round"/>
              <path d="M16 38V46C16 47.1046 16.8954 48 18 48H26" stroke="#c084fc" stroke-width="2.2" stroke-linecap="round"/>
              <path d="M48 38V46C48 47.1046 47.1046 48 46 48H38" stroke="#c084fc" stroke-width="2.2" stroke-linecap="round"/>
              <!-- Curva orgánica dermatológica con núcleo -->
              <path d="M22 34C24 28 28 27 32 31C36 35 40 33 42 29" stroke="#e0e7ff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="34" cy="38" r="3.5" fill="#c084fc" />
            </svg>
          </div>

          <h1 class="brand-title">OLIVIA</h1>
          <p class="brand-tagline">Si cuidas tu <span class="highlight-purple">piel</span>, iluminará tu futuro.</p>

          <!-- Esfera Celestial 3D Flotante con Anillos e Iluminación de Suelo -->
          <div class="celestial-system-container" id="sphereTrigger" title="Pulsa para comenzar la conversación">
            <!-- Partículas / Estrellas brillantes flotantes -->
            <div class="sparkle-particle sparkle-1">✦</div>
            <div class="sparkle-particle sparkle-2">✦</div>
            <div class="sparkle-particle sparkle-3">•</div>
            <div class="sparkle-particle sparkle-4">✦</div>
            <div class="sparkle-particle sparkle-5">•</div>

            <!-- Sistema de Esfera + Anillos 3D -->
            <div class="celestial-orb-3d-wrap">
              <!-- Anillo trasero / secundario -->
              <div class="celestial-ring ring-secondary"></div>
              
              <!-- Esfera cristalina iridiscente -->
              <div class="celestial-sphere-body">
                <div class="sphere-glow-inner"></div>
                <div class="sphere-specular-highlight"></div>
                <div class="sphere-ambient-shimmer"></div>
              </div>

              <!-- Anillo frontal / primario -->
              <div class="celestial-ring ring-primary"></div>
            </div>

            <!-- Plataforma de Luz Elíptica en el Suelo -->
            <div class="ground-light-platform">
              <div class="ground-ring ground-ring-outer"></div>
              <div class="ground-ring ground-ring-inner"></div>
              <div class="ground-beam-glow"></div>
            </div>
          </div>

          <!-- Botón Píldora Inicio -->
          <button class="start-pill-btn" id="startConversationBtn" type="button">
            <span class="pill-text">Presiona la esfera para comenzar tu conversación con Olivia</span>
            <span class="pill-chevron" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </span>
          </button>

          <!-- Footer con corazón y aviso legal -->
          <div class="landing-footer-container">
            <div class="footer-divider-heart">
              <span class="divider-line"></span>
              <span class="heart-symbol">♡</span>
              <span class="divider-line"></span>
            </div>
            <div class="legal-footnote">
              Herramienta de cribado asistida por IA · No sustituye la valoración médica
            </div>
          </div>
        </div>
      </section>

      <!-- ================= PASO 2: CONVERSACIÓN, ANÁLISIS Y PDF ================= -->
      <section class="step-container step-chat" id="step2Chat">
        <div class="chat-window">
          
          <!-- Chat Header -->
          <header class="chat-header">
            <div class="chat-header-left" id="openHistoryDrawerBtn" title="Ver historial de conversaciones">
              <div class="header-avatar">
                <div class="mini-celestial-orb"></div>
              </div>
              <div class="header-meta">
                <span class="bot-name-main">OLIVIA AI</span>
                <span class="bot-name-sub">TU ASISTENTE DERMATOLÓGICA</span>
              </div>
            </div>
            <div class="chat-header-right">
              <span class="status-pill"><span class="online-dot"></span> En línea</span>
              <button class="back-home-btn" id="backToLandingBtn" title="Volver al inicio">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                Inicio
              </button>
            </div>
          </header>

          <!-- Chat Messages Scroll Area -->
          <div class="chat-messages-area" id="chatMessagesArea">
            
            <!-- Contenedor dinámico para respuestas y resultados -->
            <div id="dynamicChatEntries"></div>

            <!-- Loader animado mientras analiza -->
            <div class="chat-msg-row bot-row" id="typingLoader" style="display: none;">
              <div class="msg-avatar"><div class="mini-celestial-orb"></div></div>
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

          <!-- Chat Floating Input Bar (Estilo Imagen 3 con botón +) -->
          <footer class="chat-floating-bar-wrapper">
            <!-- Menú desplegable flotante de acciones (+: Cámara y Subir) -->
            <div class="attach-popover-menu" id="attachPopoverMenu" style="display: none;">
              <button class="popover-action-item" id="cameraActionBtn" type="button">
                <div class="popover-icon-wrap icon-camera">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                </div>
                <div class="popover-text-meta">
                  <span class="popover-title">Cámara en vivo</span>
                  <span class="popover-subtitle">Tomar fotografía médica</span>
                </div>
              </button>
              <button class="popover-action-item" id="uploadActionBtn" type="button">
                <div class="popover-icon-wrap icon-upload">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                </div>
                <div class="popover-text-meta">
                  <span class="popover-title">Subir imagen</span>
                  <span class="popover-subtitle">Seleccionar de tu dispositivo</span>
                </div>
              </button>
            </div>

            <div class="chat-input-floating-bar">
              <!-- Botón circular '+' -->
              <button class="attach-plus-btn" id="attachPlusBtn" type="button" title="Adjuntar foto o usar cámara" aria-label="Abrir opciones de imagen">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <input type="file" id="fileInputHidden" accept="image/*" style="display: none;" />

              <form class="chat-input-form-inner" id="chatForm">
                <div class="chat-input-pill-inner">
                  <input 
                    type="text" 
                    id="chatTextInput" 
                    class="chat-text-input-field" 
                    placeholder="Escribe tu consulta médica..." 
                    autocomplete="off" 
                  />
                </div>
                <button class="send-round-btn" id="sendTextMsgBtn" type="submit" title="Enviar mensaje">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                </button>
              </form>
            </div>
          </footer>

        </div>
      </section>

    </div>

    <!-- Modal de Cámara Web / Móvil -->
    <div class="camera-modal" id="cameraModal" style="display: none;">
      <div class="camera-modal-backdrop" id="closeCameraBackdrop"></div>
      <div class="camera-modal-content">
        <div class="camera-modal-header">
          <div class="camera-title-row">
            <span class="camera-icon">📷</span>
            <div>
              <h3>Captura de Lesión Dermatológica</h3>
              <span class="camera-subtitle">Orientación médica de la Dra. Olivia</span>
            </div>
          </div>
          <button class="close-modal-btn" id="closeCameraBtn">&times;</button>
        </div>

        <!-- Guía de Buenas Prácticas Médicas para la Fotografía -->
        <div class="clinical-capture-tips">
          <div class="tips-header">
            <span>💡 Recomendaciones para máxima precisión:</span>
          </div>
          <div class="tips-grid">
            <div class="tip-item">
              <span class="tip-badge">1</span>
              <span><strong>Buena luz natural:</strong> Evita reflejos y sombras directas.</span>
            </div>
            <div class="tip-item">
              <span class="tip-badge">2</span>
              <span><strong>Distancia (~10-15 cm):</strong> Mantén el enfoque nítido sobre la lesión.</span>
            </div>
            <div class="tip-item">
              <span class="tip-badge">3</span>
              <span><strong>Ángulo perpendicular:</strong> Captura la lesión de frente, centrada.</span>
            </div>
            <div class="tip-item">
              <span class="tip-badge">4</span>
              <span><strong>Área despejada:</strong> Retira cabellos para no tapar los bordes.</span>
            </div>
          </div>
        </div>

        <div class="video-wrapper">
          <video id="webcamVideo" autoplay playsinline muted></video>
          <canvas id="webcamCanvas" style="display: none;"></canvas>
          <div class="camera-target-crosshair"></div>
        </div>
        <div class="camera-modal-actions">
          <button class="action-btn btn-camera snap-btn" id="snapPhotoBtn" type="button">📸 Tomar Foto</button>
        </div>
      </div>
    </div>

    <!-- ================= MODAL EDITOR: RECORTE (CROP) Y BRILLO ================= -->
    <div class="editor-modal" id="imageEditorModal" style="display: none;">
      <div class="editor-modal-backdrop" id="closeEditorBackdrop"></div>
      <div class="editor-modal-content">
        <div class="editor-modal-header">
          <div class="editor-title-row">
            <span class="editor-icon">✂️</span>
            <div>
              <h3>Ajuste Clínico de Imagen</h3>
              <span class="editor-subtitle">Encuadra la lesión y optimiza la iluminación</span>
            </div>
          </div>
          <button class="close-modal-btn" id="closeEditorBtn">&times;</button>
        </div>

        <div class="editor-workspace">
          <div class="editor-canvas-container" id="editorCanvasContainer">
            <canvas id="editorCanvas"></canvas>
            <div class="crop-overlay-guide">
              <div class="crop-box-border"></div>
              <span class="crop-hint-badge">Área focal de análisis</span>
            </div>
          </div>
        </div>

        <!-- Controles de Edición -->
        <div class="editor-controls-bar">
          <div class="control-group">
            <label for="brightnessSlider" class="control-label">
              <span>☀️ Brillo:</span>
              <span id="brightnessValueLabel" class="control-val-badge">0%</span>
            </label>
            <input type="range" id="brightnessSlider" min="-50" max="50" value="0" step="1" class="custom-slider" />
          </div>

          <div class="control-group">
            <label for="zoomSlider" class="control-label">
              <span>🔍 Zoom / Escala:</span>
              <span id="zoomValueLabel" class="control-val-badge">1.0x</span>
            </label>
            <input type="range" id="zoomSlider" min="1.0" max="3.5" value="1.0" step="0.05" class="custom-slider" />
          </div>
        </div>

        <div class="editor-help-text">
          <span>💡 Arrastra la imagen para centrar el lunar en el recuadro y usa el zoom si es necesario.</span>
        </div>

        <div class="editor-actions">
          <button class="action-btn btn-cancel-editor" id="cancelEditorBtn" type="button">🔄 Cancelar</button>
          <button class="action-btn btn-confirm-editor" id="confirmEditorBtn" type="button">
            <span>✅ Confirmar y Analizar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ================= PANEL LATERAL (HISTORIAL DE CHATS) ================= -->
    <div class="history-drawer" id="historyDrawer" style="display: none;">
      <div class="history-drawer-backdrop" id="closeDrawerBackdrop"></div>
      <div class="history-drawer-content">
        <div class="drawer-header">
          <div class="drawer-title-row">
            <div class="mini-orb"></div>
            <div>
              <h3 class="drawer-title">Conversaciones</h3>
              <span class="drawer-subtitle">Historial de chats guardados</span>
            </div>
          </div>
          <button class="close-modal-btn" id="closeDrawerBtn">&times;</button>
        </div>
        
        <div class="drawer-actions">
          <button class="action-btn btn-new-chat-drawer" id="drawerNewChatBtn" type="button">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            Nuevo Chat
          </button>
          <button class="action-btn btn-home-drawer" id="drawerHomeBtn" type="button">⟵ Inicio</button>
        </div>

        <div class="drawer-section-header-row">
          <div class="drawer-section-label">📋 SESIONES ANTERIORES:</div>
          <button class="btn-clear-all-drawer" id="clearAllDrawerBtn" type="button" title="Borrar todo el historial">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            Vaciar
          </button>
        </div>
        <div class="drawer-history-list" id="drawerHistoryList">
          <!-- Sesiones de chat cargadas dinámicamente -->
        </div>
      </div>
    </div>

    <script src="/static/js/app.js?v=4.2"></script>
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
            brain_memory=request.brain_memory,
        )
        return ChatMessageResponse(
            reply=reply_text,
            suggested_questions=chips,
            status=status
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en el asistente conversacional: {exc}") from exc
