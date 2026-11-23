// =============================================================================
// AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
// Copyright (c) 2026 Natalia Fuentes Sanchez
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================

// Elementos de la UI principales
const step1Landing = document.getElementById("step1Landing");
const step2Chat = document.getElementById("step2Chat");
const sphereTrigger = document.getElementById("sphereTrigger");
const startConversationBtn = document.getElementById("startConversationBtn");
const backToLandingBtn = document.getElementById("backToLandingBtn");

const fileInputHidden = document.getElementById("fileInputHidden");
const uploadActionBtn = document.getElementById("uploadActionBtn");
const cameraActionBtn = document.getElementById("cameraActionBtn");
const attachPlusBtn = document.getElementById("attachPlusBtn");
const attachPopoverMenu = document.getElementById("attachPopoverMenu");
const chatMessagesArea = document.getElementById("chatMessagesArea");
const dynamicChatEntries = document.getElementById("dynamicChatEntries");
const typingLoader = document.getElementById("typingLoader");

const newChatBtn = document.getElementById("newChatBtn");
const chatForm = document.getElementById("chatForm");
const chatTextInput = document.getElementById("chatTextInput");
const sendTextMsgBtn = document.getElementById("sendTextMsgBtn");

// Modal de Cámara
const cameraModal = document.getElementById("cameraModal");
const closeCameraBtn = document.getElementById("closeCameraBtn");
const closeCameraBackdrop = document.getElementById("closeCameraBackdrop");
const webcamVideo = document.getElementById("webcamVideo");
const webcamCanvas = document.getElementById("webcamCanvas");
const snapPhotoBtn = document.getElementById("snapPhotoBtn");

// Modal de Edición (Recorte y Brillo)
const imageEditorModal = document.getElementById("imageEditorModal");
const closeEditorBtn = document.getElementById("closeEditorBtn");
const closeEditorBackdrop = document.getElementById("closeEditorBackdrop");
const cancelEditorBtn = document.getElementById("cancelEditorBtn");
const confirmEditorBtn = document.getElementById("confirmEditorBtn");
const editorCanvas = document.getElementById("editorCanvas");
const editorCanvasContainer = document.getElementById("editorCanvasContainer");
const brightnessSlider = document.getElementById("brightnessSlider");
const brightnessValueLabel = document.getElementById("brightnessValueLabel");
const zoomSlider = document.getElementById("zoomSlider");
const zoomValueLabel = document.getElementById("zoomValueLabel");

let editorImg = new Image();
let editorScale = 1.0;
let editorBrightness = 0;
let editorPanX = 0;
let editorPanY = 0;
let isPanning = false;
let startPanX = 0;
let startPanY = 0;
let pendingFileName = "lesion.jpg";

// Panel Lateral (Cerebro e Historial)
const openHistoryDrawerBtn = document.getElementById("openHistoryDrawerBtn");
const historyDrawer = document.getElementById("historyDrawer");
const closeDrawerBtn = document.getElementById("closeDrawerBtn");
const closeDrawerBackdrop = document.getElementById("closeDrawerBackdrop");
const drawerNewChatBtn = document.getElementById("drawerNewChatBtn");
const drawerHomeBtn = document.getElementById("drawerHomeBtn");
const drawerHistoryList = document.getElementById("drawerHistoryList");
const clearAllDrawerBtn = document.getElementById("clearAllDrawerBtn");

let streamWebcam = null;
let lastAnalysisResult = null;
let chatHistory = [];
let currentSessionId = "session_" + Date.now();

// ==========================================
// GESTIÓN DE ALMACENAMIENTO DE CHATS (CEREBRO RESILIENTE)
// ==========================================
function cleanHtmlForStorage(html) {
  if (!html) return "";
  // Si contiene imágenes en Base64 pesadas, las aligeramos para evitar agotar la cuota de 5MB de localStorage
  if (html.length > 50000) {
    return html.replace(/src="data:image\/[^;]+;base64,[^"]+"/g, 'src="" data-stored-photo="true"');
  }
  return html;
}

function safeSaveSessions(savedSessions) {
  try {
    localStorage.setItem("olivia_saved_sessions", JSON.stringify(savedSessions.slice(0, 25)));
  } catch (err) {
    console.warn("Cuota de localStorage al límite. Aplicando podado inteligente de sesiones anteriores...", err);
    // Estrategia de recuperación ante cuota:
    // 1. Conservar chatHistory y resumen, eliminando entriesHtml pesado de las sesiones anteriores
    const optimized = savedSessions.map((s, idx) => {
      if (idx > 0) {
        return { ...s, entriesHtml: "" };
      }
      return s;
    });
    try {
      localStorage.setItem("olivia_saved_sessions", JSON.stringify(optimized.slice(0, 15)));
    } catch (e2) {
      // 2. Si aún persiste, conservar las 6 sesiones más recientes
      try {
        localStorage.setItem("olivia_saved_sessions", JSON.stringify(optimized.slice(0, 6)));
      } catch (e3) {
        localStorage.setItem("olivia_saved_sessions", JSON.stringify(optimized.slice(0, 3)));
      }
    }
  }
}

function saveCurrentSessionToBrain() {
  // Evitar guardar sesiones completamente vacías para no saturar el historial
  if ((!chatHistory || chatHistory.length === 0) && !lastAnalysisResult) {
    return;
  }

  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    const existingIdx = savedSessions.findIndex(s => s.id === currentSessionId);
    
    // Título descriptivo basado en el diagnóstico o primer mensaje del usuario
    let sessionTitle = "Consulta dermatológica";
    if (lastAnalysisResult && lastAnalysisResult.likely_cause) {
      sessionTitle = "Análisis: " + lastAnalysisResult.likely_cause;
    } else if (chatHistory.length > 0) {
      const firstUserMsg = chatHistory.find(m => m.sender === "user");
      if (firstUserMsg) {
        sessionTitle = firstUserMsg.text.length > 35 ? firstUserMsg.text.substring(0, 35) + "..." : firstUserMsg.text;
      }
    }

    // Generar resumen condensado de la sesión para el Cerebro de Olivia
    const keyMessages = chatHistory
      .filter(m => m.sender === "user")
      .slice(-3)
      .map(m => m.text.length > 80 ? m.text.substring(0, 80) + "..." : m.text);

    const sessionSummary = [
      sessionTitle,
      lastAnalysisResult ? `Diagnóstico: ${lastAnalysisResult.likely_cause}, Riesgo: ${Math.round((lastAnalysisResult.risk_score||0)*100)}%` : null,
      keyMessages.length > 0 ? `Consultas: ${keyMessages.join(" | ")}` : null
    ].filter(Boolean).join(". ");

    const sessionData = {
      id: currentSessionId,
      title: sessionTitle,
      dateStr: new Date().toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }),
      chatHistory: chatHistory,
      lastAnalysisResult: lastAnalysisResult ? {
        likely_cause: lastAnalysisResult.likely_cause,
        primary_label: lastAnalysisResult.primary_label,
        risk_score: lastAnalysisResult.risk_score,
        severity: lastAnalysisResult.severity,
        benign_malignant: lastAnalysisResult.benign_malignant,
        abcde_analysis: lastAnalysisResult.abcde_analysis,
        recommendation: lastAnalysisResult.recommendation
      } : null,
      summary: sessionSummary,
      entriesHtml: cleanHtmlForStorage(dynamicChatEntries ? dynamicChatEntries.innerHTML : "")
    };

    if (existingIdx >= 0) {
      savedSessions[existingIdx] = sessionData;
    } else {
      savedSessions.unshift(sessionData);
    }

    safeSaveSessions(savedSessions);
  } catch (err) {
    console.warn("No se pudo guardar la sesión en Cerebro de Olivia:", err);
  }
}

/**
 * Construye el texto de memoria condensada de las últimas sesiones previas
 * para inyectarlo en el prompt de Gemini como Cerebro de Olivia.
 */
function buildBrainMemorySummary() {
  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    // Excluir la sesión actual y tomar las 5 más recientes
    const pastSessions = savedSessions.filter(s => s.id !== currentSessionId).slice(0, 5);
    if (pastSessions.length === 0) return null;

    const lines = pastSessions.map((s, i) =>
      `Sesión ${i + 1} (${s.dateStr}): ${s.summary || s.title}`
    );
    return lines.join("\n");
  } catch {
    return null;
  }
}

function deleteSessionFromBrain(sessionId) {
  try {
    let savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    savedSessions = savedSessions.filter(s => s.id !== sessionId);
    safeSaveSessions(savedSessions);
    
    // Si la sesión eliminada era la que estaba en pantalla, reiniciar a nuevo chat
    if (currentSessionId === sessionId) {
      resetChatSession();
    }
    loadBrainHistoryList();
  } catch (err) {
    console.warn("Error al eliminar la sesión:", err);
  }
}

function loadBrainHistoryList() {
  if (!drawerHistoryList) return;
  drawerHistoryList.innerHTML = "";
  
  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    
    if (savedSessions.length === 0) {
      drawerHistoryList.innerHTML = `<div class="drawer-empty-msg">Aún no hay conversaciones guardadas.<br/>¡Empieza a hablar con la Dra. Olivia!</div>`;
      return;
    }

    savedSessions.forEach(session => {
      const isActive = session.id === currentSessionId;
      const card = document.createElement("div");
      card.className = "drawer-session-card" + (isActive ? " active-session" : "");
      card.innerHTML = `
        <div class="session-card-info">
          <div class="session-card-header">
            <span class="session-card-title">${session.title}</span>
            <span class="session-card-date">${session.dateStr}</span>
          </div>
          <div class="session-card-preview">${session.chatHistory ? session.chatHistory.length : 0} mensajes · ${isActive ? '<strong style="color:#818cf8">Sesión actual</strong>' : 'Pulsa para restaurar'}</div>
        </div>
        <button class="delete-session-btn" title="Eliminar este chat" type="button" aria-label="Eliminar conversación">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      `;
      
      // Restaurar al hacer clic en la tarjeta
      card.addEventListener("click", () => restoreSessionFromBrain(session.id));

      // Botón de papelera para borrar este chat individual
      const delBtn = card.querySelector(".delete-session-btn");
      if (delBtn) {
        delBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          deleteSessionFromBrain(session.id);
        });
      }

      drawerHistoryList.appendChild(card);
    });
  } catch (err) {
    drawerHistoryList.innerHTML = `<div class="drawer-empty-msg">Error al cargar el historial de chats.</div>`;
  }
}

function restoreSessionFromBrain(sessionId) {
  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    const session = savedSessions.find(s => s.id === sessionId);
    if (!session) return;

    currentSessionId = session.id;
    lastAnalysisResult = session.lastAnalysisResult || null;
    chatHistory = session.chatHistory || [];
    
    if (dynamicChatEntries) {
      if (session.entriesHtml && session.entriesHtml.trim() !== "") {
        dynamicChatEntries.innerHTML = session.entriesHtml;
      } else if (session.chatHistory && session.chatHistory.length > 0) {
        // Reconstrucción desde el historial de mensajes
        dynamicChatEntries.innerHTML = "";
        session.chatHistory.forEach(msg => {
          const row = document.createElement("div");
          row.className = "chat-msg-row " + (msg.sender === "user" ? "user-row" : "bot-row");
          if (msg.sender === "user") {
            row.innerHTML = `<div class="msg-bubble user-bubble"><p>${msg.text}</p></div>`;
          } else {
            row.innerHTML = `
              <div class="msg-avatar"><div class="mini-celestial-orb"></div></div>
              <div class="msg-bubble bot-bubble">${parseSimpleMarkdown(msg.text)}</div>
            `;
          }
          dynamicChatEntries.appendChild(row);
        });
        if (lastAnalysisResult) {
          appendBotResultCard(lastAnalysisResult);
        }
      }
    }
    
    closeDrawer();
    goToChat();
    scrollToBottom();
  } catch (err) {
    alert("No se pudo restaurar la sesión seleccionada.");
  }
}
    alert("No se pudo restaurar la sesión seleccionada.");
  }
}

function openDrawer() {
  loadBrainHistoryList();
  if (historyDrawer) {
    historyDrawer.style.display = "flex";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        historyDrawer.classList.add("drawer-open");
      });
    });
  }
}

function closeDrawer() {
  if (historyDrawer) {
    historyDrawer.classList.remove("drawer-open");
    setTimeout(() => {
      if (!historyDrawer.classList.contains("drawer-open")) {
        historyDrawer.style.display = "none";
      }
    }, 310);
  }
}

function toggleDrawer() {
  if (historyDrawer && historyDrawer.classList.contains("drawer-open")) {
    closeDrawer();
  } else {
    openDrawer();
  }
}

if (openHistoryDrawerBtn) openHistoryDrawerBtn.addEventListener("click", toggleDrawer);
if (closeDrawerBtn) closeDrawerBtn.addEventListener("click", closeDrawer);
if (closeDrawerBackdrop) closeDrawerBackdrop.addEventListener("click", closeDrawer);

if (drawerNewChatBtn) {
  drawerNewChatBtn.addEventListener("click", () => {
    closeDrawer();
    setTimeout(resetChatSession, 320);
  });
}

if (drawerHomeBtn) {
  drawerHomeBtn.addEventListener("click", () => {
    closeDrawer();
    setTimeout(goToLanding, 320);
  });
}

if (clearAllDrawerBtn) {
  clearAllDrawerBtn.addEventListener("click", () => {
    if (confirm("¿Estás segura de que deseas vaciar todas las conversaciones guardadas del historial?")) {
      localStorage.removeItem("olivia_saved_sessions");
      resetChatSession();
      loadBrainHistoryList();
    }
  });
}

// ==========================================
// CONTROL DE NAVEGACIÓN (PASO 1 <-> PASO 2)
// ==========================================
function goToChat() {
  step1Landing.classList.remove("active");
  step2Chat.classList.add("active");
  if (dynamicChatEntries && dynamicChatEntries.children.length === 0) {
    resetChatSession();
  }
  scrollToBottom();
}

function goToLanding() {
  step2Chat.classList.remove("active");
  step1Landing.classList.add("active");
}

if (sphereTrigger) sphereTrigger.addEventListener("click", goToChat);
if (startConversationBtn) startConversationBtn.addEventListener("click", goToChat);
if (backToLandingBtn) backToLandingBtn.addEventListener("click", goToLanding);

// Función para ocultar la tarjeta de bienvenida al iniciar la interacción
function hideWelcomeCardIfPresent() {
  const welcomeRow = document.querySelector(".welcome-card-row");
  if (welcomeRow) {
    welcomeRow.remove();
  }
}

// ==========================================
// FUNCIÓN PARA CREAR / REINICIAR NUEVO CHAT
// ==========================================
function resetChatSession() {
  currentSessionId = "session_" + Date.now();
  if (dynamicChatEntries) dynamicChatEntries.innerHTML = "";
  lastAnalysisResult = null;
  chatHistory = [];
  
  const msgRow = document.createElement("div");
  msgRow.className = "chat-msg-row bot-row welcome-card-row";
  msgRow.innerHTML = `
    <div class="welcome-glass-card">
      <!-- Marca de agua médica sutil -->
      <div class="card-cross-watermark" aria-hidden="true">
        <svg width="86" height="86" viewBox="0 0 64 64" fill="none">
          <path d="M26 12H38V26H52V38H38V52H26V38H12V26H26V12Z" stroke="rgba(139, 92, 246, 0.2)" stroke-width="2.5" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Cabecera de la tarjeta con badge tecnológico y texto -->
      <div class="welcome-card-header">
        <div class="welcome-tech-badge" aria-hidden="true">
          <div class="badge-ring-orbit"></div>
          <svg class="badge-camera-svg" viewBox="0 0 64 64" fill="none">
            <path d="M16 26V18C16 16.8954 16.8954 16 18 16H26" stroke="#c084fc" stroke-width="2.4" stroke-linecap="round"/>
            <path d="M48 26V18C48 16.8954 47.1046 16 46 16H38" stroke="#c084fc" stroke-width="2.4" stroke-linecap="round"/>
            <path d="M16 38V46C16 47.1046 16.8954 48 18 48H26" stroke="#c084fc" stroke-width="2.4" stroke-linecap="round"/>
            <path d="M48 38V46C48 47.1046 47.1046 48 46 48H38" stroke="#c084fc" stroke-width="2.4" stroke-linecap="round"/>
            <circle cx="32" cy="32" r="5" fill="#c084fc" />
          </svg>
        </div>

        <div class="welcome-header-text">
          <h2 class="welcome-card-title"><span class="purple-sparkle">✦</span> ¡Nuevo chat iniciado!</h2>
          <p class="welcome-card-desc">Soy la <strong class="dr-olivia-highlight">Dra. Olivia</strong>, tu médica asistencial de orientación dermatológica.</p>
          <p class="welcome-card-subdesc">Puedes preguntarme cualquier duda sobre tu piel, síntomas o subir una fotografía para analizarla:</p>
        </div>
      </div>

      <!-- Tres opciones guía informativas (no interactivas) -->
      <div class="welcome-guide-options">
        <div class="guide-action-pill" id="guideOptionText">
          <div class="pill-icon-circle">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          </div>
          <span class="guide-text">Escribe tus preguntas o dudas médicas directamente abajo.</span>
        </div>

        <div class="guide-action-pill" id="guideOptionCamera">
          <div class="pill-icon-circle">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
          </div>
          <span class="guide-text">Pulsa el botón <strong class="badge-highlight-camera">+</strong> y elige <strong>Cámara</strong> para tomar una foto en directo.</span>
        </div>

        <div class="guide-action-pill" id="guideOptionUpload">
          <div class="pill-icon-circle">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
          </div>
          <span class="guide-text">Pulsa el botón <strong class="badge-highlight-upload">+</strong> y elige <strong>Subir</strong> para seleccionar una imagen de tu dispositivo.</span>
        </div>
      </div>
    </div>
  `;
  dynamicChatEntries.appendChild(msgRow);

  scrollToBottom();
  saveCurrentSessionToBrain();
}

if (newChatBtn) {
  newChatBtn.addEventListener("click", resetChatSession);
}

// ==========================================
// FORMATEADOR DE MARKDOWN Y JERARQUÍA CHAT
// ==========================================
function parseSimpleMarkdown(text) {
  if (!text) return "";
  
  let str = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  str = str.replace(/^###\s+(.+)$/gm, '<h4 class="chat-heading-h4">$1</h4>');
  str = str.replace(/^##\s+(.+)$/gm, '<h3 class="chat-heading-h3">$1</h3>');
  str = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  str = str.replace(/\*(.*?)\*/g, '<em>$1</em>');
  str = str.replace(/^[\*•]\s+(.+)$/gm, '<div class="chat-bullet-item"><span class="chat-bullet-icon">✦</span><span class="chat-bullet-txt">$1</span></div>');
  str = str.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="chat-num-item"><span class="chat-num-badge">$1</span><div class="chat-num-content">$2</div></div>');

  const lines = str.split("\n\n");
  const formattedParagraphs = lines.map(block => {
    block = block.trim();
    if (block.startsWith("<h") || block.startsWith("<div")) {
      return block;
    }
    return `<p class="chat-paragraph">${block.replace(/\n/g, "<br/>")}</p>`;
  });

  return formattedParagraphs.join("");
}

// ==========================================
// MANEJO DE ENTRADA DE TEXTO Y GEMINI CHAT
// ==========================================
async function handleUserTextMessage(text) {
  if (!text) return;
  
  // Ocultar la tarjeta de bienvenida al enviar el primer mensaje
  hideWelcomeCardIfPresent();
  
  const userRow = document.createElement("div");
  userRow.className = "chat-msg-row user-row";
  userRow.innerHTML = `
    <div class="msg-bubble user-bubble">
      <p>${text}</p>
    </div>
  `;
  dynamicChatEntries.appendChild(userRow);
  chatHistory.push({ sender: "user", text: text });
  scrollToBottom();
  saveCurrentSessionToBrain();

  const lower = text.toLowerCase();
  if (
    lower.includes("nuevo chat") || 
    lower.includes("abrir un nuevo chat") || 
    lower.includes("reiniciar") || 
    lower.includes("limpiar") ||
    lower.includes("otro chat") ||
    lower.includes("reset")
  ) {
    setTimeout(() => {
      resetChatSession();
    }, 400);
    return;
  }

  if (typingLoader) typingLoader.style.display = "flex";
  scrollToBottom();

  try {
    const payload = {
      message: text,
      history: chatHistory.slice(-8),
      brain_memory: buildBrainMemorySummary(),
      analysis_context: lastAnalysisResult ? {
        "diagnóstico_principal": {
          etiqueta_es: lastAnalysisResult.likely_cause,
          codigo: lastAnalysisResult.primary_label,
          confianza_porcentaje: Math.round((lastAnalysisResult.risk_score || 0) * 100)
        },
        gravedad: {
          nivel: lastAnalysisResult.severity,
          descripcion: lastAnalysisResult.benign_malignant === "maligno_probable" ? "Lesión con signos de malignidad" : "Lesión con patrón benigno",
          porcentaje_gravedad: Math.round((lastAnalysisResult.risk_score || 0) * 100)
        },
        regla_abcde: lastAnalysisResult.abcde_analysis,
        derivacion: {
          prioridad: lastAnalysisResult.referral,
          mensaje: lastAnalysisResult.recommendation
        }
      } : null
    };

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (typingLoader) typingLoader.style.display = "none";

    if (!res.ok) {
      appendBotErrorMessage("Lo siento, tuve un pequeño problema al procesar tu consulta. Por favor inténtalo de nuevo.");
      return;
    }

    const data = await res.json();
    chatHistory.push({ sender: "olivia", text: data.reply });
    appendOliviaChatBubble(data.reply, data.suggested_questions);
    saveCurrentSessionToBrain();

  } catch (err) {
    if (typingLoader) typingLoader.style.display = "none";
    appendBotErrorMessage("Error de conexión con el servicio conversacional de la Dra. Olivia.");
  }
}

function appendOliviaChatBubble(replyText, suggestedQuestions) {
  const botRow = document.createElement("div");
  botRow.className = "chat-msg-row bot-row";

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "msg-bubble olivia-reply-bubble";
  bubbleDiv.innerHTML = parseSimpleMarkdown(replyText);

  if (suggestedQuestions && suggestedQuestions.length > 0) {
    const chipsContainer = document.createElement("div");
    chipsContainer.className = "quick-chips-container";

    const chipsLabel = document.createElement("span");
    chipsLabel.className = "chips-label";
    chipsLabel.textContent = "💡 Sugerencias de consulta:";
    chipsContainer.appendChild(chipsLabel);

    const chipsWrapper = document.createElement("div");
    chipsWrapper.className = "chips-wrapper";

    suggestedQuestions.forEach((q) => {
      const btn = document.createElement("button");
      btn.className = "chip-btn";
      btn.type = "button";
      btn.textContent = q;
      btn.addEventListener("click", () => {
        if (chatTextInput) chatTextInput.value = "";
        handleUserTextMessage(q);
      });
      chipsWrapper.appendChild(btn);
    });

    chipsContainer.appendChild(chipsWrapper);
    bubbleDiv.appendChild(chipsContainer);
  }

  botRow.innerHTML = `<div class="msg-avatar"><div class="mini-orb"></div></div>`;
  botRow.appendChild(bubbleDiv);

  dynamicChatEntries.appendChild(botRow);
  scrollToBottom();
}

if (chatForm) {
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = chatTextInput.value.trim();
    if (val) {
      chatTextInput.value = "";
      handleUserTextMessage(val);
    }
  });
}

// ==========================================
// MANEJO DE ENTRADA: BOTÓN '+' Y POPOVER DE ACCIONES
// ==========================================
function toggleAttachPopover(show) {
  if (!attachPopoverMenu) return;
  const isCurrentlyOpen = attachPopoverMenu.style.display !== "none";
  const shouldOpen = show !== undefined ? show : !isCurrentlyOpen;
  attachPopoverMenu.style.display = shouldOpen ? "flex" : "none";
  if (attachPlusBtn) {
    if (shouldOpen) {
      attachPlusBtn.classList.add("active");
    } else {
      attachPlusBtn.classList.remove("active");
    }
  }
}

if (attachPlusBtn) {
  attachPlusBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleAttachPopover();
  });
}

// Cerrar el popover al hacer clic fuera
document.addEventListener("click", (e) => {
  if (attachPopoverMenu && attachPopoverMenu.style.display !== "none") {
    if (!attachPopoverMenu.contains(e.target) && !attachPlusBtn.contains(e.target)) {
      toggleAttachPopover(false);
    }
  }
});

if (uploadActionBtn) {
  uploadActionBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleAttachPopover(false);
    fileInputHidden.click();
  });
}

if (fileInputHidden) {
  fileInputHidden.addEventListener("change", (e) => {
    if (!e.target.files || !e.target.files.length) return;
    const file = e.target.files[0];
    openImageEditor(file);
  });
}

if (cameraActionBtn) {
  cameraActionBtn.addEventListener("click", async (e) => {
    e.stopPropagation();
    toggleAttachPopover(false);
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      fileInputHidden.click();
      return;
    }

    try {
      cameraModal.style.display = "flex";
      streamWebcam = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      webcamVideo.srcObject = streamWebcam;
    } catch (err) {
      closeWebcam();
      fileInputHidden.click();
    }
  });
}

function closeWebcam() {
  if (streamWebcam) {
    streamWebcam.getTracks().forEach(track => track.stop());
    streamWebcam = null;
  }
  if (cameraModal) cameraModal.style.display = "none";
}

if (closeCameraBtn) closeCameraBtn.addEventListener("click", closeWebcam);
if (closeCameraBackdrop) closeCameraBackdrop.addEventListener("click", closeWebcam);

if (snapPhotoBtn) {
  snapPhotoBtn.addEventListener("click", () => {
    if (!webcamVideo.videoWidth) return;
    webcamCanvas.width = webcamVideo.videoWidth;
    webcamCanvas.height = webcamVideo.videoHeight;
    const ctx = webcamCanvas.getContext("2d");
    ctx.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);
    
    webcamCanvas.toBlob((blob) => {
      closeWebcam();
      const capturedFile = new File([blob], "captura_camara.jpg", { type: "image/jpeg" });
      openImageEditor(capturedFile);
    }, "image/jpeg", 0.95);
  });
}

// ==========================================
// EDITOR INTERACTIVO: RECORTE Y BRILLO
// ==========================================
function openImageEditor(file) {
  pendingFileName = file.name || "captura.jpg";
  const reader = new FileReader();
  reader.onload = (e) => {
    editorImg = new Image();
    editorImg.onload = () => {
      editorScale = 1.0;
      editorBrightness = 0;
      editorPanX = 0;
      editorPanY = 0;
      if (brightnessSlider) brightnessSlider.value = 0;
      if (brightnessValueLabel) brightnessValueLabel.textContent = "0%";
      if (zoomSlider) zoomSlider.value = 1.0;
      if (zoomValueLabel) zoomValueLabel.textContent = "1.0x";
      
      initEditorCanvas();
      if (imageEditorModal) imageEditorModal.style.display = "flex";
    };
    editorImg.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function closeImageEditor() {
  if (imageEditorModal) imageEditorModal.style.display = "none";
  if (fileInputHidden) fileInputHidden.value = "";
}

if (closeEditorBtn) closeEditorBtn.addEventListener("click", closeImageEditor);
if (closeEditorBackdrop) closeEditorBackdrop.addEventListener("click", closeImageEditor);
if (cancelEditorBtn) cancelEditorBtn.addEventListener("click", closeImageEditor);

function initEditorCanvas() {
  if (!editorCanvas || !editorImg.width) return;
  const containerSize = editorCanvasContainer ? editorCanvasContainer.clientWidth || 320 : 320;
  editorCanvas.width = containerSize;
  editorCanvas.height = containerSize;
  renderEditor();
}

function renderEditor() {
  if (!editorCanvas || !editorImg.width) return;
  const ctx = editorCanvas.getContext("2d");
  const cw = editorCanvas.width;
  const ch = editorCanvas.height;

  ctx.clearRect(0, 0, cw, ch);
  ctx.save();

  // Calcular ajuste para cubrir el recuadro (cover)
  const baseScale = Math.max(cw / editorImg.width, ch / editorImg.height);
  const currentScale = baseScale * editorScale;

  const drawW = editorImg.width * currentScale;
  const drawH = editorImg.height * currentScale;

  const cx = cw / 2 + editorPanX;
  const cy = ch / 2 + editorPanY;

  ctx.drawImage(editorImg, cx - drawW / 2, cy - drawH / 2, drawW, drawH);

  // Aplicar ajuste de brillo pixel a pixel directo (100% compatible con todos los navegadores)
  if (editorBrightness !== 0) {
    const imgData = ctx.getImageData(0, 0, cw, ch);
    const d = imgData.data;
    const factor = Number(editorBrightness) * 1.8; // escala perceptible [-90, +90]
    for (let i = 0; i < d.length; i += 4) {
      d[i] = Math.min(255, Math.max(0, d[i] + factor));
      d[i + 1] = Math.min(255, Math.max(0, d[i + 1] + factor));
      d[i + 2] = Math.min(255, Math.max(0, d[i + 2] + factor));
    }
    ctx.putImageData(imgData, 0, 0);
  }

  ctx.restore();
}

// Control de Brillo
if (brightnessSlider) {
  brightnessSlider.addEventListener("input", (e) => {
    editorBrightness = Number(e.target.value);
    if (brightnessValueLabel) {
      brightnessValueLabel.textContent = (editorBrightness > 0 ? "+" : "") + editorBrightness + "%";
    }
    renderEditor();
  });
}

// Control de Zoom
if (zoomSlider) {
  zoomSlider.addEventListener("input", (e) => {
    editorScale = Number(e.target.value);
    if (zoomValueLabel) {
      zoomValueLabel.textContent = editorScale.toFixed(1) + "x";
    }
    renderEditor();
  });
}

// Soporte de Arrastre (Pan) con ratón y táctil
if (editorCanvasContainer) {
  const onPointerDown = (clientX, clientY) => {
    isPanning = true;
    startPanX = clientX - editorPanX;
    startPanY = clientY - editorPanY;
  };

  const onPointerMove = (clientX, clientY) => {
    if (!isPanning) return;
    editorPanX = clientX - startPanX;
    editorPanY = clientY - startPanY;
    renderEditor();
  };

  const onPointerUp = () => {
    isPanning = false;
  };

  editorCanvasContainer.addEventListener("mousedown", (e) => onPointerDown(e.clientX, e.clientY));
  window.addEventListener("mousemove", (e) => onPointerMove(e.clientX, e.clientY));
  window.addEventListener("mouseup", onPointerUp);

  editorCanvasContainer.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) {
      onPointerDown(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  window.addEventListener("touchmove", (e) => {
    if (e.touches.length === 1) {
      onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  window.addEventListener("touchend", onPointerUp);

  // Zoom con rueda de ratón sobre el canvas
  editorCanvasContainer.addEventListener("wheel", (e) => {
    e.preventDefault();
    const delta = e.deltaY * -0.002;
    editorScale = Math.min(3.5, Math.max(1.0, editorScale + delta));
    if (zoomSlider) zoomSlider.value = editorScale;
    if (zoomValueLabel) zoomValueLabel.textContent = editorScale.toFixed(1) + "x";
    renderEditor();
  }, { passive: false });
}

// Confirmar y Analizar: Generar recorte en alta resolución
if (confirmEditorBtn) {
  confirmEditorBtn.addEventListener("click", () => {
    if (!editorImg.width) return;

    // Crear canvas de salida de alta fidelidad (mínimo 448x448 para análisis)
    const outCanvas = document.createElement("canvas");
    const outSize = Math.max(448, Math.min(editorImg.width, editorImg.height));
    outCanvas.width = outSize;
    outCanvas.height = outSize;
    const outCtx = outCanvas.getContext("2d");

    outCtx.filter = `brightness(${100 + Number(editorBrightness)}%)`;

    const cw = editorCanvas.width;
    const ch = editorCanvas.height;
    const baseScale = Math.max(cw / editorImg.width, ch / editorImg.height);
    const currentScale = baseScale * editorScale;

    const drawW = editorImg.width * currentScale;
    const drawH = editorImg.height * currentScale;
    const cx = cw / 2 + editorPanX;
    const cy = ch / 2 + editorPanY;

    // Mapear al tamaño de salida
    const ratio = outSize / cw;
    outCtx.drawImage(
      editorImg,
      (cx - drawW / 2) * ratio,
      (cy - drawH / 2) * ratio,
      drawW * ratio,
      drawH * ratio
    );

    // Aplicar el mismo ajuste de brillo pixel a pixel al resultado final
    if (editorBrightness !== 0) {
      const outImgData = outCtx.getImageData(0, 0, outSize, outSize);
      const od = outImgData.data;
      const factor = Number(editorBrightness) * 1.8;
      for (let i = 0; i < od.length; i += 4) {
        od[i] = Math.min(255, Math.max(0, od[i] + factor));
        od[i + 1] = Math.min(255, Math.max(0, od[i + 1] + factor));
        od[i + 2] = Math.min(255, Math.max(0, od[i + 2] + factor));
      }
      outCtx.putImageData(outImgData, 0, 0);
    }

    outCanvas.toBlob((blob) => {
      closeImageEditor();
      const croppedFile = new File([blob], pendingFileName, { type: "image/jpeg" });
      processSelectedImage(croppedFile);
    }, "image/jpeg", 0.94);
  });
}

// ==========================================
// ENVÍO Y PROCESAMIENTO CON RESNET-18
// ==========================================
function scrollToBottom() {
  setTimeout(() => {
    if (chatMessagesArea) chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;
  }, 50);
}

function appendUserImageMessage(imageSrc, fileName) {
  // Ocultar la tarjeta de bienvenida al enviar la primera foto
  hideWelcomeCardIfPresent();

  const msgRow = document.createElement("div");
  msgRow.className = "chat-msg-row user-row";
  msgRow.innerHTML = `
    <div class="msg-bubble user-bubble">
      <p>Foto enviada para análisis: <strong>${fileName}</strong></p>
      <img src="${imageSrc}" class="user-image-preview" alt="Lesión subida" />
    </div>
  `;
  dynamicChatEntries.appendChild(msgRow);
  scrollToBottom();
}

async function processSelectedImage(file) {
  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64DataUrl = e.target.result;
    appendUserImageMessage(base64DataUrl, file.name);
    
    if (typingLoader) typingLoader.style.display = "flex";
    scrollToBottom();
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      if (typingLoader) typingLoader.style.display = "none";

      if (!response.ok) {
        appendBotErrorMessage("Lo siento, ocurrió un problema al procesar la imagen: " + (data.detail || "Error del servidor"));
        return;
      }

      if (!data.image_base64) {
        data.image_base64 = base64DataUrl;
      }
      lastAnalysisResult = data;
      appendBotResultCard(data);
      saveCurrentSessionToBrain();

      setTimeout(() => {
        const diagName = data.likely_cause || "tu lesión";
        appendOliviaChatBubble(
          `He completado el análisis dermatológico de tu imagen. 😊\n\nHe detectado signos compatibles con **${diagName}**. ` +
          "Puedes consultar todos los detalles en la tarjeta de arriba o hacerme cualquier pregunta directamente aquí. " +
          "¿Tienes alguna duda sobre este resultado?",
          [
            `¿Qué cuidados debo tener con ${diagName}?`,
            "¿Por qué es importante la regla ABCDE?",
            "¿Qué le pregunto a mi dermatólogo?"
          ]
        );
        saveCurrentSessionToBrain();
      }, 500);

    } catch (err) {
      if (typingLoader) typingLoader.style.display = "none";
      appendBotErrorMessage("Error de conexión con el servidor de análisis dermatológico.");
    }
  };
  reader.readAsDataURL(file);
}

function appendBotErrorMessage(text) {
  const msgRow = document.createElement("div");
  msgRow.className = "chat-msg-row bot-row";
  msgRow.innerHTML = `
    <div class="msg-avatar"><div class="mini-orb"></div></div>
    <div class="msg-bubble" style="border: 1px solid #f87171; color: #fca5a5;">
      ${text}
    </div>
  `;
  dynamicChatEntries.appendChild(msgRow);
  scrollToBottom();
}

function toggleGradCamViewer(btn) {
  const container = btn.closest(".gradcam-section-block")?.querySelector(".gradcam-container");
  if (!container) return;
  const isHidden = container.style.display === "none";
  container.style.display = isHidden ? "block" : "none";
  const label = btn.querySelector("span") || btn;
  label.textContent = isHidden ? "Ocultar mapa de calor" : "Mostrar mapa de calor";
  scrollToBottom();
}

function appendBotResultCard(data) {
  const text = data.user_report || "";
  const abcde = data.abcde_analysis || {};

  let stateVisual = data.primary_label === "sano" ? "SANO / BENIGNO" : "ENFERMO / MALIGNO";
  let stateColorClass = "val-green";
  if (text.includes("SANO / BENIGNO")) {
    stateVisual = "SANO / BENIGNO";
    stateColorClass = "val-green";
  } else if (text.includes("ENFERMO / PREMALIGNO")) {
    stateVisual = "ENFERMO / PREMALIGNO";
    stateColorClass = "val-amber";
  } else if (text.includes("ENFERMO / MALIGNO")) {
    stateVisual = "ENFERMO / MALIGNO";
    stateColorClass = "val-red";
  }

  let alertText = "BAJO RIESGO";
  let alertColorClass = "val-green";
  if (text.includes("Nivel de alerta: GRAVE")) {
    alertText = "GRAVE";
    alertColorClass = "val-red";
  } else if (text.includes("Nivel de alerta: MODERADO")) {
    alertText = "MODERADO";
    alertColorClass = "val-amber";
  } else if (text.includes("Nivel de alerta: LEVE - MODERADO")) {
    alertText = "LEVE - MODERADO";
    alertColorClass = "val-amber";
  }

  const matchClass = text.match(/• Clasificación de la lesión:\s*(.+)/);
  const classification = matchClass ? matchClass[1].trim() : (data.benign_malignant === "benigno_probable" ? "Benigna / Normal" : "Maligna probable");

  const matchCompat = text.match(/• Compatibilidad estimada:\s*(.+)/);
  const compatPct = matchCompat ? matchCompat[1].trim() : `${Math.round(data.risk_score * 100)}%`;

  const matchPatology = text.match(/• Patología más compatible:\s*(.+)/);
  const patologyName = matchPatology ? matchPatology[1].trim() : data.likely_cause;

  const matchDesc = text.match(/DESCRIPCIÓN Y CONTEXTO\s*\n([\s\S]*?)(?=\n\nEVALUACIÓN VISUAL)/);
  const description = matchDesc ? matchDesc[1].trim() : "";

  const matchRec = text.match(/RECOMENDACIÓN Y DERIVACIÓN\s*\n([\s\S]*?)$/);
  const recommendation = matchRec ? matchRec[1].trim() : data.recommendation;

  const matchPhototype = text.match(/• Fototipo cutáneo:\s*(.+)/);
  const phototypeVal = data.phototype
    ? `${data.phototype.fitzpatrick_type} (${data.phototype.skin_category} · ITA: ${data.phototype.ita_angle}°)`
    : (matchPhototype ? matchPhototype[1].trim() : "Fototipo III (Piel Intermedia)");

  const ptObj = data.phototype || {
    fitzpatrick_type: "Fototipo III",
    fitzpatrick_scale: "III",
    ita_angle: 32.0,
    skin_category: "Piel Media / Intermedia",
    burn_tendency: "Moderada (se quema al inicio de temporada)",
    tan_tendency: "Gradual (se broncea progresivamente)",
    recommended_spf: "FPS 30 - 50",
    sun_protection_advice: "Aplicar fotoprotector FPS 30-50 antes de exposiciones al aire libre. Reaplicar cada 2 horas y no descuidar la protección en días nublados."
  };

  const msgRow = document.createElement("div");
  msgRow.className = "chat-msg-row bot-row";
  
  msgRow.innerHTML = `
    <div class="msg-avatar"><div class="mini-orb"></div></div>
    <div class="result-card-bubble">
      <div class="result-card-header">RESULTADO DEL ANÁLISIS DE LA RED NEURONAL</div>
      
      <div class="result-field-list">
        <div class="field-item">
          <span class="field-label">• Estado visual:</span>
          <span class="field-val ${stateColorClass}">${stateVisual}</span>
        </div>
        <div class="field-item">
          <span class="field-label">• Nivel de alerta:</span>
          <span class="field-val ${alertColorClass}">${alertText} (${compatPct})</span>
        </div>
        <div class="field-item">
          <span class="field-label">• Clasificación de la lesión:</span>
          <span class="field-val">${classification}</span>
        </div>
        <div class="field-item">
          <span class="field-label">• Patología más compatible:</span>
          <span class="field-val" style="color: #c084fc;">${patologyName}</span>
        </div>
        <div class="field-item">
          <span class="field-label">• Fototipo cutáneo estimado:</span>
          <span class="field-val" style="color: #fbbf24;">${phototypeVal}</span>
        </div>
      </div>

      ${description ? `
      <div class="section-block">
        <div class="section-heading">DESCRIPCIÓN Y CONTEXTO</div>
        <div class="section-text">${description}</div>
      </div>
      ` : ''}

      <div class="section-block">
        <div class="section-heading">EVALUACIÓN VISUAL (Criterios ABCDE)</div>
        <div class="abcde-chat-list">
          <div class="abcde-row">
            <span class="abcde-badge badge-a">A</span>
            <div class="abcde-row-content">
              <span class="abcde-row-title">Asimetría</span>
              <span class="abcde-row-desc">${abcde.asymmetry_desc || 'Sin datos de asimetría'}</span>
            </div>
          </div>
          <div class="abcde-row">
            <span class="abcde-badge badge-b">B</span>
            <div class="abcde-row-content">
              <span class="abcde-row-title">Bordes</span>
              <span class="abcde-row-desc">${abcde.border_desc || 'Sin datos de bordes'}</span>
            </div>
          </div>
          <div class="abcde-row">
            <span class="abcde-badge badge-c">C</span>
            <div class="abcde-row-content">
              <span class="abcde-row-title">Color</span>
              <span class="abcde-row-desc">${abcde.color_desc || 'Sin datos de color'}</span>
            </div>
          </div>
          <div class="abcde-row">
            <span class="abcde-badge badge-d">D</span>
            <div class="abcde-row-content">
              <span class="abcde-row-title">Diámetro</span>
              <span class="abcde-row-desc">${abcde.diameter_desc || 'Sin datos de diámetro'}</span>
            </div>
          </div>
          <div class="abcde-row">
            <span class="abcde-badge badge-e">E</span>
            <div class="abcde-row-content">
              <span class="abcde-row-title">Estructura</span>
              <span class="abcde-row-desc">${abcde.structure_desc || 'Sin datos de estructura'}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="section-block phototype-section-block">
        <div class="phototype-header-row">
          <div class="section-heading">☀️ FOTOTIPO CUTÁNEO (FITZPATRICK) & PREVENCIÓN SOLAR</div>
          <span class="phototype-pill-badge badge-fitz-${ptObj.fitzpatrick_scale.toLowerCase()}">
            ${ptObj.fitzpatrick_type} (ITA: ${ptObj.ita_angle}°)
          </span>
        </div>
        <div class="phototype-details-grid">
          <div class="phototype-meta-item">
            <span class="pt-label">Clasificación cutánea:</span>
            <span class="pt-value">${ptObj.skin_category}</span>
          </div>
          <div class="phototype-meta-item">
            <span class="pt-label">Fotoprotección mínima:</span>
            <span class="pt-value highlight-spf">${ptObj.recommended_spf}</span>
          </div>
          <div class="phototype-meta-item">
            <span class="pt-label">Reactividad solar:</span>
            <span class="pt-value">${ptObj.burn_tendency}</span>
          </div>
          <div class="phototype-meta-item">
            <span class="pt-label">Capacidad de bronceado:</span>
            <span class="pt-value">${ptObj.tan_tendency}</span>
          </div>
        </div>
        <div class="phototype-advice-box">
          <div class="phototype-advice-title">🛡️ Pautas preventivas personalizadas de fotoprotección:</div>
          <p class="phototype-advice-text">${ptObj.sun_protection_advice}</p>
        </div>
      </div>

      <div class="section-block" style="border-left-color: ${alertColorClass === 'val-red' ? '#f43f5e' : (alertColorClass === 'val-amber' ? '#f59e0b' : '#10b981')};">
        <div class="section-heading">RECOMENDACIÓN Y DERIVACIÓN</div>
        <div class="section-text" style="color: #f1f5f9; font-weight: 500;">${recommendation}</div>
      </div>

      ${data.gradcam_image_base64 ? `
      <div class="section-block gradcam-section-block">
        <div class="gradcam-header-row">
          <div class="section-heading">🔍 EXPLICABILIDAD IA (GRAD-CAM)</div>
          <button type="button" class="gradcam-toggle-btn" onclick="toggleGradCamViewer(this)">
            <span>Mostrar mapa de calor</span>
          </button>
        </div>
        <div class="gradcam-container" style="display: none;">
          <div class="gradcam-visual-wrapper">
            <div class="gradcam-image-box">
              <span class="gradcam-img-caption">Foto original</span>
              <img src="${data.image_base64 || ''}" alt="Foto original" class="gradcam-thumb" />
            </div>
            <div class="gradcam-image-box">
              <span class="gradcam-img-caption">Zonas de interés IA</span>
              <img src="${data.gradcam_image_base64}" alt="Mapa Grad-CAM" class="gradcam-thumb gradcam-active-thumb" />
            </div>
          </div>
          <p class="gradcam-description-text">
            Este mapa de calor térmico (Grad-CAM) resalta en tonos cálidos (rojo/amarillo) las regiones morfológicas que más influyeron en la activación de la red neuronal para este diagnóstico.
          </p>
        </div>
      </div>
      ` : ''}

      <button class="pdf-download-interactive-btn" type="button" onclick="triggerPdfDownload()">
        <span>📥 ¿Deseas descargar tu informe clínico completo en PDF?</span>
      </button>
    </div>
  `;

  dynamicChatEntries.appendChild(msgRow);
  scrollToBottom();
}

// ==========================================
// EXPORTACIÓN DE INFORME PDF
// ==========================================
async function triggerPdfDownload() {
  if (!lastAnalysisResult) {
    alert("No hay datos de análisis disponibles para generar el PDF.");
    return;
  }

  try {
    const res = await fetch("/download-report-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastAnalysisResult)
    });

    if (!res.ok) {
      throw new Error("Error al generar el archivo PDF en el servidor.");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `informe_clinico_olivia_${lastAnalysisResult.filename.split('.')[0] || 'analisis'}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert("No se pudo descargar el informe PDF: " + err.message);
  }
}
window.triggerPdfDownload = triggerPdfDownload;

// Inicialización de sesión al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  if (dynamicChatEntries && dynamicChatEntries.children.length === 0) {
    resetChatSession();
  }
});
