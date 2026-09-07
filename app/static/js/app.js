// =============================================================================
// AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
// Copyright (c) 2026 Natalia Fuentes Sanchez
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================

const inputEl = document.getElementById("img");
const resultEl = document.getElementById("result");
const buttonEl = document.getElementById("analyzeButton");
const uploadBtn = document.getElementById("uploadBtn");
const analysisTextEl = document.getElementById("analysisText");
const resultPanelEl = document.getElementById("resultPanel");
const jsonBoxEl = document.getElementById("jsonBox");
const previewCard = document.getElementById("previewCard");
const previewImg = document.getElementById("previewImg");

function setPendingState() {
  buttonEl.disabled = true;
  buttonEl.textContent = "Analizando con Red Neuronal...";
  analysisTextEl.textContent = "Procesando imagen con ResNet-18 y calculando diagnóstico...";
  resultPanelEl.style.display = "block";
  jsonBoxEl.style.display = "none";
}

function resetButtonState() {
  buttonEl.disabled = false;
  buttonEl.textContent = "Analizar ahora";
}

function openFilePicker() {
  inputEl.click();
}

function renderStructuredReport(data) {
  const text = data.user_report || "";
  const abcde = data.abcde_analysis || {};
  
  // Determinamos el color temático según el nivel de alerta / gravedad
  let alertBadgeClass = "badge-low";
  let alertText = "BAJO RIESGO";
  let stateText = data.primary_label === "sano" ? "SANO / BENIGNO" : "ENFERMO";
  let severity = (data.severity || "").toLowerCase();

  if (text.includes("Nivel de alerta: GRAVE") || severity === "grave") {
    alertBadgeClass = "badge-danger";
    alertText = "GRAVE";
  } else if (text.includes("Nivel de alerta: MODERADO")) {
    alertBadgeClass = "badge-warning";
    alertText = "MODERADO";
  } else if (text.includes("Nivel de alerta: LEVE - MODERADO") || severity === "medio") {
    alertBadgeClass = "badge-moderate";
    alertText = "LEVE - MODERADO";
  }

  // Parseo de campos de la plantilla
  const matchState = text.match(/• Estado visual:\s*(.+)/);
  if (matchState) stateText = matchState[1].trim();

  const matchClassification = text.match(/• Clasificación de la lesión:\s*(.+)/);
  const classificationText = matchClassification ? matchClassification[1].trim() : (data.benign_malignant === "benigno_probable" ? "Benigna / Normal" : "Maligna probable");

  const matchCompat = text.match(/• Compatibilidad estimada:\s*(.+)/);
  const compatText = matchCompat ? matchCompat[1].trim() : `${Math.round(data.risk_score * 100)}%`;

  const matchPatology = text.match(/• Patología más compatible:\s*(.+)/);
  const patologyText = matchPatology ? matchPatology[1].trim() : data.likely_cause;

  const matchDesc = text.match(/DESCRIPCIÓN Y CONTEXTO\s*\n([\s\S]*?)(?=\n\nEVALUACIÓN VISUAL)/);
  const descText = matchDesc ? matchDesc[1].trim() : "";

  const matchRec = text.match(/RECOMENDACIÓN Y DERIVACIÓN\s*\n([\s\S]*?)$/);
  const recText = matchRec ? matchRec[1].trim() : data.recommendation;

  const html = `
    <div class="clinical-report-container">
      <!-- 1. CABECERA Y RESULTADOS PRINCIPALES -->
      <div class="report-section-header">
        <span class="report-main-title">RESULTADO DEL ANÁLISIS DE LA RED NEURONAL</span>
        <span class="alert-badge ${alertBadgeClass}">${alertText}</span>
      </div>

      <div class="report-grid-metrics">
        <div class="metric-card">
          <div class="metric-lbl">Estado visual</div>
          <div class="metric-val ${stateText.includes('SANO') ? 'val-safe' : (stateText.includes('PREMALIGNO') ? 'val-premalign' : 'val-danger')}">${stateText}</div>
        </div>
        <div class="metric-card">
          <div class="metric-lbl">Clasificación de la lesión</div>
          <div class="metric-val">${classificationText}</div>
        </div>
        <div class="metric-card">
          <div class="metric-lbl">Compatibilidad estimada</div>
          <div class="metric-val metric-pct">${compatText}</div>
        </div>
        <div class="metric-card highlight-metric">
          <div class="metric-lbl">Patología más compatible</div>
          <div class="metric-val val-patology">${patologyText}</div>
        </div>
      </div>

      <!-- 2. DESCRIPCIÓN Y CONTEXTO -->
      <div class="report-block">
        <div class="block-title">📋 DESCRIPCIÓN Y CONTEXTO</div>
        <div class="block-body">${descText || 'Descripción visual de la lesión analizada.'}</div>
      </div>

      <!-- 3. EVALUACIÓN VISUAL (CRITERIOS ABCDE) -->
      <div class="report-block">
        <div class="block-title">🔬 EVALUACIÓN VISUAL (Criterios ABCDE)</div>
        <div class="abcde-grid">
          <div class="abcde-item">
            <span class="abcde-letter">A</span>
            <div class="abcde-info">
              <strong>Asimetría:</strong>
              <span>${abcde.asymmetry_desc || 'Evaluación simétrica'}</span>
            </div>
          </div>
          <div class="abcde-item">
            <span class="abcde-letter">B</span>
            <div class="abcde-info">
              <strong>Bordes:</strong>
              <span>${abcde.border_desc || 'Bordes circunscritos'}</span>
            </div>
          </div>
          <div class="abcde-item">
            <span class="abcde-letter">C</span>
            <div class="abcde-info">
              <strong>Color:</strong>
              <span>${abcde.color_desc || 'Coloración regular'}</span>
            </div>
          </div>
          <div class="abcde-item">
            <span class="abcde-letter">D</span>
            <div class="abcde-info">
              <strong>Diámetro:</strong>
              <span>${abcde.diameter_desc || 'Diámetro focal'}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. RECOMENDACIÓN Y DERIVACIÓN -->
      <div class="report-block recommendation-block ${alertBadgeClass === 'badge-danger' ? 'rec-urgent' : (alertBadgeClass === 'badge-moderate' ? 'rec-warning' : 'rec-routine')}">
        <div class="block-title">🏥 RECOMENDACIÓN Y DERIVACIÓN</div>
        <div class="block-body rec-body">${recText || data.recommendation}</div>
      </div>
    </div>
  `;

  analysisTextEl.innerHTML = html;
}

async function sendImage() {
  if (!inputEl.files || !inputEl.files.length) {
    analysisTextEl.textContent = "Por favor, selecciona una imagen primero.";
    resultPanelEl.style.display = "block";
    jsonBoxEl.style.display = "none";
    return;
  }

  const fileToSend = inputEl.files[0];
  const fd = new FormData();
  fd.append("file", fileToSend);

  setPendingState();
  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    const data = await res.json();

    if (!res.ok) {
      analysisTextEl.textContent = "Ha ocurrido un error al procesar la imagen.";
      resultEl.textContent = JSON.stringify(data, null, 2);
      jsonBoxEl.style.display = "block";
      return;
    }

    renderStructuredReport(data);
    resultEl.textContent = JSON.stringify(data, null, 2);
    jsonBoxEl.style.display = "block";
    resultPanelEl.style.display = "block";
  } catch (error) {
    analysisTextEl.textContent = "No se pudo conectar con el servidor.";
    resultEl.textContent = `Error de red: ${error}`;
    jsonBoxEl.style.display = "block";
  } finally {
    resetButtonState();
  }
}


inputEl.addEventListener("change", () => {
  if (!inputEl.files.length) return;

  const file = inputEl.files[0];
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewCard.style.display = "flex";
  };
  reader.readAsDataURL(file);

  analysisTextEl.textContent = `Imagen '${file.name}' cargada. Haz clic en 'Analizar ahora'.`;
  resultPanelEl.style.display = "block";
  jsonBoxEl.style.display = "none";
});

uploadBtn.addEventListener("click", openFilePicker);
buttonEl.addEventListener("click", sendImage);
