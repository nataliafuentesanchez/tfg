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

// Panel Lateral (Cerebro e Historial)
const openHistoryDrawerBtn = document.getElementById("openHistoryDrawerBtn");
const historyDrawer = document.getElementById("historyDrawer");
const closeDrawerBtn = document.getElementById("closeDrawerBtn");
const closeDrawerBackdrop = document.getElementById("closeDrawerBackdrop");
const drawerNewChatBtn = document.getElementById("drawerNewChatBtn");
const drawerHomeBtn = document.getElementById("drawerHomeBtn");
const drawerHistoryList = document.getElementById("drawerHistoryList");

let streamWebcam = null;
let lastAnalysisResult = null;
let chatHistory = [];
let currentSessionId = "session_" + Date.now();

// ==========================================
// GESTIÓN DE ALMACENAMIENTO DE CHATS (CEREBRO)
// ==========================================
function saveCurrentSessionToBrain() {
  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    const existingIdx = savedSessions.findIndex(s => s.id === currentSessionId);
    
    // Titulo descriptivo basado en el ultimo mensaje o diagnostico
    let sessionTitle = "Consulta dermatológica";
    if (lastAnalysisResult && lastAnalysisResult.likely_cause) {
      sessionTitle = "Análisis: " + lastAnalysisResult.likely_cause;
    } else if (chatHistory.length > 0) {
      const firstUserMsg = chatHistory.find(m => m.sender === "user");
      if (firstUserMsg) {
        sessionTitle = firstUserMsg.text.length > 30 ? firstUserMsg.text.substring(0, 30) + "..." : firstUserMsg.text;
      }
    }

    const sessionData = {
      id: currentSessionId,
      title: sessionTitle,
      dateStr: new Date().toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }),
      chatHistory: chatHistory,
      lastAnalysisResult: lastAnalysisResult,
      entriesHtml: dynamicChatEntries ? dynamicChatEntries.innerHTML : ""
    };

    if (existingIdx >= 0) {
      savedSessions[existingIdx] = sessionData;
    } else {
      savedSessions.unshift(sessionData);
    }

    localStorage.setItem("olivia_saved_sessions", JSON.stringify(savedSessions.slice(0, 20)));
  } catch (err) {
    console.warn("No se pudo guardar la sesión en Cerebro de Olivia:", err);
  }
}

function loadBrainHistoryList() {
  if (!drawerHistoryList) return;
  drawerHistoryList.innerHTML = "";
  
  try {
    const savedSessions = JSON.parse(localStorage.getItem("olivia_saved_sessions") || "[]");
    
    if (savedSessions.length === 0) {
      drawerHistoryList.innerHTML = `<div class="drawer-empty-msg">No hay chats anteriores guardados. ¡Empieza a conversar con la Dra. Olivia!</div>`;
      return;
    }

    savedSessions.forEach(session => {
      const card = document.createElement("div");
      card.className = "drawer-session-card" + (session.id === currentSessionId ? " active-session" : "");
      card.innerHTML = `
        <div class="session-card-header">
          <span class="session-card-title">${session.title}</span>
          <span class="session-card-date">${session.dateStr}</span>
        </div>
        <div class="session-card-preview">${session.chatHistory ? session.chatHistory.length : 0} mensajes guardados</div>
      `;
      card.addEventListener("click", () => restoreSessionFromBrain(session.id));
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
      dynamicChatEntries.innerHTML = session.entriesHtml || "";
    }
    
    closeDrawer();
    goToChat();
    scrollToBottom();
  } catch (err) {
    alert("No se pudo restaurar la sesión seleccionada.");
  }
}

function openDrawer() {
  loadBrainHistoryList();
  if (historyDrawer) historyDrawer.style.display = "flex";
}

function closeDrawer() {
  if (historyDrawer) historyDrawer.style.display = "none";
}

if (openHistoryDrawerBtn) openHistoryDrawerBtn.addEventListener("click", openDrawer);
if (closeDrawerBtn) closeDrawerBtn.addEventListener("click", closeDrawer);
if (closeDrawerBackdrop) closeDrawerBackdrop.addEventListener("click", closeDrawer);

if (drawerNewChatBtn) {
  drawerNewChatBtn.addEventListener("click", () => {
    closeDrawer();
    resetChatSession();
  });
}

if (drawerHomeBtn) {
  drawerHomeBtn.addEventListener("click", () => {
    closeDrawer();
    goToLanding();
  });
}

// ==========================================
// CONTROL DE NAVEGACIÓN (PASO 1 <-> PASO 2)
// ==========================================
function goToChat() {
  step1Landing.classList.remove("active");
  step2Chat.classList.add("active");
  scrollToBottom();
}

function goToLanding() {
  step2Chat.classList.remove("active");
  step1Landing.classList.add("active");
}

if (sphereTrigger) sphereTrigger.addEventListener("click", goToChat);
if (startConversationBtn) startConversationBtn.addEventListener("click", goToChat);
if (backToLandingBtn) backToLandingBtn.addEventListener("click", goToLanding);

// ==========================================
// FUNCIÓN PARA CREAR / REINICIAR NUEVO CHAT
// ==========================================
function resetChatSession() {
  currentSessionId = "session_" + Date.now();
  if (dynamicChatEntries) dynamicChatEntries.innerHTML = "";
  lastAnalysisResult = null;
  chatHistory = [];
  
  const msgRow = document.createElement("div");
  msgRow.className = "chat-msg-row bot-row";
  msgRow.innerHTML = `
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
      analysis_context: lastAnalysisResult ? {
        diagnóstico_principal: {
          etiqueta_es: lastAnalysisResult.likely_cause,
          codigo: lastAnalysisResult.primary_label,
          confianza_porcentaje: Math.round(lastAnalysisResult.confidence * 100)
        },
        gravedad: {
          nivel: lastAnalysisResult.severity,
          descripcion: lastAnalysisResult.severity_desc,
          porcentaje_gravedad: lastAnalysisResult.severity_pct
        },
        regla_abcde: lastAnalysisResult.abcde_analysis,
        derivacion: {
          prioridad: lastAnalysisResult.urgency,
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
// MANEJO DE ENTRADA: ARCHIVO O CÁMARA
// ==========================================
if (uploadActionBtn) {
  uploadActionBtn.addEventListener("click", () => {
    fileInputHidden.click();
  });
}

if (fileInputHidden) {
  fileInputHidden.addEventListener("change", (e) => {
    if (!e.target.files || !e.target.files.length) return;
    const file = e.target.files[0];
    processSelectedImage(file);
  });
}

if (cameraActionBtn) {
  cameraActionBtn.addEventListener("click", async () => {
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
      processSelectedImage(capturedFile);
    }, "image/jpeg", 0.92);
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

      <div class="section-block" style="border-left-color: ${alertColorClass === 'val-red' ? '#f43f5e' : (alertColorClass === 'val-amber' ? '#f59e0b' : '#10b981')};">
        <div class="section-heading">RECOMENDACIÓN Y DERIVACIÓN</div>
        <div class="section-text" style="color: #f1f5f9; font-weight: 500;">${recommendation}</div>
      </div>

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
