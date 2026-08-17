from torchvision.datasets import EuroSAT
from sklearn.model_selection import train_test_split
import json
import os

dataset = EuroSAT(root="data/raw", download=True)

print("Classes:", dataset.classes)
print("Total images:", len(dataset))

os.makedirs("data/processed", exist_ok=True)

indices = list(range(len(dataset)))
labels = [dataset[i][1] for i in indices]

train_idx, temp_idx = train_test_split(
    indices, test_size=0.3, stratify=labels, random_state=42
)
val_idx, test_idx = train_test_split(
    temp_idx, test_size=0.5, stratify=[labels[i] for i in temp_idx], random_state=42
)

splits = {"train": train_idx, "val": val_idx, "test": test_idx}
with open("data/processed/splits.json", "w") as f:
    json.dump(splits, f)

print("Split saved:", {k: len(v) for k, v in splits.items()})