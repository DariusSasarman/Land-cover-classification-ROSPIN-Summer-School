import os

import torch
import torch.nn as nn
from torchvision.models import resnet18

from app.logger import get_logger
from app.ml_engine.ModelDownloader import download_model_weights

logger = get_logger("ml_engine.SpectralResNet18")

NUM_BANDS = 13
NUM_CLASSES = 10
INPUT_SIZE = 224


class ResNet18_M3(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = resnet18(weights=None)
        self.model.conv1 = nn.Conv2d(
            NUM_BANDS, 64, kernel_size=7, stride=2, padding=3, bias=False
        )
        self.model.fc = nn.Linear(self.model.fc.in_features, NUM_CLASSES)

    def forward(self, x):
        return self.model(x)

    @staticmethod
    def get_instance():
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights_path = os.path.join(
            os.path.dirname(__file__), "spectral_resnet_torchgeo_best.pth"
        )
        download_model_weights(os.path.dirname(__file__))
        checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
        model = ResNet18_M3().to(device)
        state_dict = checkpoint["model_state_dict"]
        if not any(key.startswith("model.") for key in state_dict):
            state_dict = {f"model.{key}": value for key, value in state_dict.items()}
        model.load_state_dict(state_dict)
        model.eval()
        logger.info(
            "Loaded 13-band Sentinel-2 ResNet-18 from %s (val_accuracy=%.4f)",
            weights_path,
            checkpoint.get("val_accuracy", float("nan")),
        )
        return model
