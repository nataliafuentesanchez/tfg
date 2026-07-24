// =============================================================================
// AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
// Copyright (c) 2026 Natalia Fuentes Sanchez
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================

const inputEl = document.getElementById("img");
const fileNameEl = document.getElementById("fileName");
const reportEl = document.getElementById("report");
const resultEl = document.getElementById("result");
const buttonEl = document.getElementById("analyzeButton");

function setPendingState() {
  buttonEl.disabled = true;
  buttonEl.textContent = "Analizando...";
  reportEl.textContent = "Informe legible: procesando imagen...";
}

function resetButtonState() {
  buttonEl.disabled = false;
  buttonEl.textContent = "Analizar ahora";
}

async function sendImage() {
  if (!inputEl.files.length) {
    reportEl.textContent = "Informe legible: selecciona una imagen para iniciar el analisis.";
    resultEl.textContent = "Selecciona una imagen.";
    return;
  }

  const fd = new FormData();
  fd.append("file", inputEl.files[0]);

  setPendingState();
  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    const data = await res.json();

    if (!res.ok) {
      reportEl.textContent = "Informe legible: ha ocurrido un error al procesar la imagen.";
      resultEl.textContent = JSON.stringify(data, null, 2);
      return;
    }

    reportEl.textContent = `Informe legible: ${data.user_report || "No disponible."}`;
    resultEl.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    reportEl.textContent = "Informe legible: no se pudo conectar con el servidor.";
    resultEl.textContent = `Error de red: ${error}`;
  } finally {
    resetButtonState();
  }
}

inputEl.addEventListener("change", () => {
  if (!inputEl.files.length) {
    fileNameEl.textContent = "Arrastra o selecciona una imagen";
    return;
  }

  fileNameEl.textContent = `Archivo seleccionado: ${inputEl.files[0].name}`;
});

buttonEl.addEventListener("click", sendImage);
