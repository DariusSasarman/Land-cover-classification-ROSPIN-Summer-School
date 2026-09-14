from typing import Dict

import torch
from PIL import Image
from torchvision.models import ResNet18_Weights

from app.ml_engine.ResNet18M3 import ResNet18_M3
from app.ml_engine.EurosatClasses import EUROSAT_CLASS_ORDER
from app.logger import get_logger

logger = get_logger("ml_engine.LandCoverClassifier")

_TRANSFORM = ResNet18_Weights.DEFAULT.transforms()


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

    def classify(self, image: Image.Image) -> Dict[str, float]:
        tensor = _TRANSFORM(image.convert("RGB")).unsqueeze(0).to(self._device)

        with torch.no_grad():
            logits = self._model(tensor)
            probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu()

        return {
            class_id: round(probabilities[i].item() * 100, 1)
            for i, class_id in enumerate(EUROSAT_CLASS_ORDER)
        }