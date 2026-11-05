# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import os
import pytest
import numpy as np
import cv2
import torch
from torchvision import models
from app.services.gradcam_service import GradCAMService
from app.services.inference_service import analyze_image


def test_gradcam_service_generates_heatmap_and_overlay():
    # Instanciar una ResNet de prueba
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 7)
    model.eval()

    gradcam = GradCAMService(model)
    
    # Crear tensor ficticio (1, 3, 224, 224)
    dummy_input = torch.randn(1, 3, 224, 224)
    heatmap = gradcam.generate_heatmap(dummy_input, target_class_idx=0)
    
    assert heatmap is not None
    assert heatmap.shape == (7, 7)
    assert np.min(heatmap) >= 0.0
    assert np.max(heatmap) <= 1.0

    # Probar generacion de overlay base64 con imagen simulada
    dummy_bgr = np.zeros((224, 224, 3), dtype=np.uint8)
    b64_str = gradcam.generate_gradcam_overlay_base64(dummy_input, dummy_bgr, target_class_idx=0)
    
    assert b64_str is not None
    assert b64_str.startswith("data:image/png;base64,")
    
    gradcam.remove_hooks()


def test_analyze_image_returns_gradcam_field():
    # Crear una imagen sintética dermatológica (círculo oscuro sobre fondo piel)
    img = np.full((300, 300, 3), (180, 200, 230), dtype=np.uint8) # tono piel BGR
    cv2.circle(img, (150, 150), 50, (30, 40, 60), -1) # lesión oscura
    _, encoded = cv2.imencode(".jpg", img)
    content = encoded.tobytes()

    result = analyze_image(content, filename="synthetic_lesion.jpg")
    
    assert result is not None
    assert hasattr(result, "gradcam_image_base64")
    # Si el modelo convolucional está cargado, debe generar el Grad-CAM
    if os.path.exists(os.path.join(os.getcwd(), "models", "best_skin_cnn.pth")):
        assert result.gradcam_image_base64 is not None
        assert result.gradcam_image_base64.startswith("data:image/png;base64,")

