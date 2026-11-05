# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

import base64
from io import BytesIO
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn


class GradCAMService:
    """Servicio para calcular mapas de activación de clases ponderados por gradiente (Grad-CAM)."""

    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        self.model = model
        # Por defecto en ResNet, target_layer suele ser model.layer4
        if target_layer is None and hasattr(model, "layer4"):
            self.target_layer = model.layer4
        else:
            self.target_layer = target_layer

        self.gradients = None
        self.activations = None
        self._handles = []
        self._register_hooks()

    def _register_hooks(self):
        if self.target_layer is None:
            return

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        def forward_hook(module, input, output):
            self.activations = output.detach()

        self._handles.append(self.target_layer.register_forward_hook(forward_hook))
        self._handles.append(self.target_layer.register_full_backward_hook(backward_hook))

    def remove_hooks(self):
        for handle in self._handles:
            handle.remove()
        self._handles = []

    def generate_heatmap(
        self,
        input_tensor: torch.Tensor,
        target_class_idx: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """Calcula el mapa de activación Grad-CAM 2D normalizado [0, 1]."""
        if self.target_layer is None:
            return None

        self.model.eval()
        self.gradients = None
        self.activations = None

        # Habilitar gradientes de forma controlada para backward
        input_tensor = input_tensor.clone().requires_grad_(True)
        logits = self.model(input_tensor)

        if target_class_idx is None:
            target_class_idx = int(torch.argmax(logits, dim=1).item())

        score = logits[0, target_class_idx]
        self.model.zero_grad()
        score.backward(retain_graph=False)

        if self.gradients is None or self.activations is None:
            return None

        # Global average pooling de los gradientes por canal
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0]

        for i in range(activations.size(0)):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)  # ReLU sobre las activaciones

        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val
        else:
            heatmap = np.zeros_like(heatmap)

        return heatmap

    def generate_gradcam_overlay_base64(
        self,
        input_tensor: torch.Tensor,
        original_image_bgr: np.ndarray,
        target_class_idx: Optional[int] = None,
        alpha: float = 0.55
    ) -> Optional[str]:
        """Genera la imagen con heatmap superpuesto y la devuelve en Base64."""
        try:
            heatmap = self.generate_heatmap(input_tensor, target_class_idx)
            if heatmap is None:
                return None

            h, w = original_image_bgr.shape[:2]
            heatmap_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_LINEAR)
            heatmap_uint8 = np.uint8(255 * heatmap_resized)

            # Aplicar mapa de color JET (azul = frio/bajo, rojo = caliente/alta atencion)
            color_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

            # Superposicion ponderada (blending)
            overlay = cv2.addWeighted(color_heatmap, alpha, original_image_bgr, 1.0 - alpha, 0)

            # Codificar a PNG en memoria
            success, buffer = cv2.imencode(".png", overlay)
            if not success:
                return None

            b64_str = base64.b64encode(buffer).decode("utf-8")
            return f"data:image/png;base64,{b64_str}"
        except Exception as e:
            print(f"Error generando Grad-CAM: {e}")
            return None

