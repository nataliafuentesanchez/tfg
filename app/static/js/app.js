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
const cameraBtn = document.getElementById("cameraBtn");
const analysisTextEl = document.getElementById("analysisText");
const resultPanelEl = document.getElementById("resultPanel");
const jsonBoxEl = document.getElementById("jsonBox");

function setPendingState() {
  buttonEl.disabled = true;
  buttonEl.textContent = "Analizando...";
  analysisTextEl.textContent = "Procesando imagen y preparando el informe...";
  resultPanelEl.hidden = false;
}

function resetButtonState() {
  buttonEl.disabled = false;
  buttonEl.textContent = "Analizar ahora";
}

function openFilePicker() {
  inputEl.click();
}

async function sendImage() {
  if (!inputEl.files.length) {
    analysisTextEl.textContent = "Selecciona una imagen para iniciar el análisis.";
    resultPanelEl.hidden = false;
    jsonBoxEl.hidden = true;
    return;
  }

  const fd = new FormData();
  fd.append("file", inputEl.files[0]);

  setPendingState();
  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    const data = await res.json();

    if (!res.ok) {
      analysisTextEl.textContent = "Ha ocurrido un error al procesar la imagen.";
      resultEl.textContent = JSON.stringify(data, null, 2);
      jsonBoxEl.hidden = false;
      return;
    }

    analysisTextEl.textContent = data.user_report || "No disponible.";
    resultEl.textContent = JSON.stringify(data, null, 2);
    jsonBoxEl.hidden = false;
    resultPanelEl.hidden = false;
  } catch (error) {
    analysisTextEl.textContent = "No se pudo conectar con el servidor.";
    resultEl.textContent = `Error de red: ${error}`;
    jsonBoxEl.hidden = false;
  } finally {
    resetButtonState();
  }
}

inputEl.addEventListener("change", () => {
  if (!inputEl.files.length) {
    return;
  }

  if (analysisTextEl.textContent === "No hay análisis todavía.") {
    analysisTextEl.textContent = "Imagen preparada. Pulsa analizar para obtener el informe.";
    resultPanelEl.hidden = false;
  }
});

uploadBtn.addEventListener("click", openFilePicker);
cameraBtn.addEventListener("click", openFilePicker);
buttonEl.addEventListener("click", sendImage);
