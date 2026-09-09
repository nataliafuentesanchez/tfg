// =============================================================================
// AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
// Copyright (c) 2026 Natalia Fuentes Sanchez
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================

// Elementos de la UI
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

// Modal de Cámara
const cameraModal = document.getElementById("cameraModal");
const closeCameraBtn = document.getElementById("closeCameraBtn");
const closeCameraBackdrop = document.getElementById("closeCameraBackdrop");
const webcamVideo = document.getElementById("webcamVideo");
const webcamCanvas = document.getElementById("webcamCanvas");
const snapPhotoBtn = document.getElementById("snapPhotoBtn");

let streamWebcam = null;
let lastAnalysisResult = null;

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
    try {
      cameraModal.style.display = "flex";
      streamWebcam = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      webcamVideo.srcObject = streamWebcam;
    } catch (err) {
      alert("No se pudo acceder a la cámara: " + err.message);
      closeWebcam();
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
    appendUserImageMessage(e.target.result, file.name);
    
    // Mostrar loader de Olivia
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

      lastAnalysisResult = data;
      appendBotResultCard(data);
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

  // Estado visual
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

  // Nivel de alerta
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

  // Clasificación
  const matchClass = text.match(/• Clasificación de la lesión:\s*(.+)/);
  const classification = matchClass ? matchClass[1].trim() : (data.benign_malignant === "benigno_probable" ? "Benigna / Normal" : "Maligna probable");

  // Compatibilidad
  const matchCompat = text.match(/• Compatibilidad estimada:\s*(.+)/);
  const compatPct = matchCompat ? matchCompat[1].trim() : `${Math.round(data.risk_score * 100)}%`;

  // Patología más compatible
  const matchPatology = text.match(/• Patología más compatible:\s*(.+)/);
  const patologyName = matchPatology ? matchPatology[1].trim() : data.likely_cause;

  // Descripción y Contexto
  const matchDesc = text.match(/DESCRIPCIÓN Y CONTEXTO\s*\n([\s\S]*?)(?=\n\nEVALUACIÓN VISUAL)/);
  const description = matchDesc ? matchDesc[1].trim() : "";

  // Recomendación
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
