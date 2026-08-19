import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# 1. Load patches
try:
    rgb_patches = np.load("data/processed/tiles/patches_rgb.npy")
    print(f"Successfully loaded {len(rgb_patches)} patches.")
except FileNotFoundError:
    print("Error: Could not find patches. Run tile_and_prepare_inference.py first!")
    exit()

# 2. Define Model 
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

# 3. Load the trained weights
checkpoint_path = "checkpoints/resnet18_m3_best.pth"
model = ResNet18_M3().to(DEVICE)
model.load_state_dict(torch.load(checkpoint_path, map_location=DEVICE)["model_state_dict"])
model.eval()

# 4. Normalize the satellite pixels to look like standard photos
rgb_float = rgb_patches.astype(np.float32)
p98 = np.percentile(rgb_float, 98)
rgb_norm = np.clip(rgb_float / p98, 0, 1)

# Convert to PyTorch tensor and apply ImageNet normalization
tensor_patches = torch.tensor(rgb_norm).float()
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
tensor_patches = normalize(tensor_patches)

# 5. Run Batch Inference
predictions = []
BATCH_SIZE = 32

print("Running model predictions...")
with torch.no_grad():
    for i in range(0, len(tensor_patches), BATCH_SIZE):
        batch = tensor_patches[i : i + BATCH_SIZE].to(DEVICE)
        outputs = model(batch)
        preds = outputs.argmax(dim=1).cpu().numpy()
        predictions.extend(preds)

# 6. Save final predictions
predictions_array = np.array(predictions)
np.save("data/processed/tiles/predictions.npy", predictions_array)
print(f"Inference complete! {len(predictions_array)} predictions saved to data/processed/tiles/predictions.npy")