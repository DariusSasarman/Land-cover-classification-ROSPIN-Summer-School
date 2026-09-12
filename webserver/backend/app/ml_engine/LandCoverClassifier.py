from typing import Dict

import torch
import numpy as np
import torch.nn.functional as F

from app.ml_engine.ResNet18M3 import ResNet18_M3
from app.ml_engine.EurosatClasses import EUROSAT_CLASS_ORDER
from app.logger import get_logger

logger = get_logger("ml_engine.LandCoverClassifier")

class LandCoverClassifier:
    _instance = None

    def __init__(self):
        logger.info("Initializing LandCoverClassifier singleton...")
        self._model = ResNet18_M3.get_instance()
        self._device = next(self._model.parameters()).device
        logger.info("LandCoverClassifier loaded on target device: %s", self._device)

    @classmethod
    def get_instance(cls) -> "LandCoverClassifier":
        if cls._instance is None:
            cls._instance = LandCoverClassifier()
        return cls._instance

    def classify(self, bands: np.ndarray) -> Dict[str, float]:
        if bands.ndim != 3 or bands.shape[-1] != 13:
            raise ValueError(
                f"Expected an HWC 13-band Sentinel-2 tile, got {bands.shape}"
            )

        # Copernicus REFLECTANCE values are already scaled to [0, 1].
        tensor = torch.from_numpy(bands).permute(2, 0, 1).float()
        tensor = F.interpolate(
            tensor.unsqueeze(0),
            size=(224, 224),
            mode="bilinear",
            align_corners=False,
        ).to(self._device)

        with torch.no_grad():
            logits = self._model(tensor)
            probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu()

        return {
            class_id: round(probabilities[i].item() * 100, 1)
            for i, class_id in enumerate(EUROSAT_CLASS_ORDER)
        }