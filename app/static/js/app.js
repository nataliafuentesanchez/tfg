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

    analysisTextEl.textContent = data.user_report || "No disponible.";
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
