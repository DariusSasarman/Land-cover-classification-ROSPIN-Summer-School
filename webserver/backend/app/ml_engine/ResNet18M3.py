from app.ml_engine.ModelDownloader import download_model_weights
import torch
import torch.nn as nn
import numpy as np
import os
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights

class ResNet18_M3(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.model.fc = nn.Sequential(
            nn.Linear(self.model.fc.in_features, 200),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(200, 100),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(100, 10)
        )
    def forward(self, x):
        return self.model(x)

    @staticmethod
    def get_instance():

        download_model_weights(os.path.dirname(__file__))

        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights_path = os.path.join(os.path.dirname(__file__), "resnet18_m3_best.pth")
    
        model = ResNet18_M3().to(DEVICE)
    
        checkpoint = torch.load(
            weights_path,
            map_location=DEVICE,
            weights_only=False
        )
    
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
    
        return model
