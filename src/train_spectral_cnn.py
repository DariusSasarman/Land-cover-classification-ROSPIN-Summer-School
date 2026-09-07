"""Train a multispectral ResNet on the 13-band EuroSAT dataset.

Unlike train_spectral_rf.py, this model keeps the spatial structure of each
64x64 patch instead of reducing every band to summary statistics.

The existing data/processed/splits.json file is reused so the result can be
compared fairly with the RGB Random Forest and ResNet reports.
"""

import argparse
import json
import os
import random
from contextlib import nullcontext

import numpy as np
import rasterio
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader, Dataset
from torchvision.models import ResNet18_Weights, resnet18


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLBANDS_ROOT = os.path.join(REPO_ROOT, "data", "raw", "EuroSATallBands")
SPLITS_PATH = os.path.join(REPO_ROOT, "data", "processed", "splits.json")
REPORT_PATH = os.path.join(REPO_ROOT, "reports", "spectral_cnn_report.txt")
CHECKPOINT_PATH = os.path.join(REPO_ROOT, "checkpoints", "spectral_resnet_best.pth")

BAND_ORDER = [
    "B01", "B02", "B03", "B04", "B05", "B06", "B07",
    "B08", "B08A", "B09", "B10", "B11", "B12",
]
CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway",
    "Industrial", "Pasture", "PermanentCrop", "Residential",
    "River", "SeaLake",
]


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def find_samples():
    class_dirs = {}
    for dirpath, _, filenames in os.walk(ALLBANDS_ROOT):
        class_name = os.path.basename(dirpath)
        if class_name in CLASS_NAMES and any(
            name.lower().endswith(".tif") for name in filenames
        ):
            class_dirs[class_name] = dirpath

    missing = set(CLASS_NAMES) - set(class_dirs)
    if missing:
        raise FileNotFoundError(
            f"Missing classes {sorted(missing)} under {ALLBANDS_ROOT}. "
            "Run src/download_eurosat_allbands.py first."
        )

    samples = []
    for class_name in sorted(CLASS_NAMES):
        for filename in sorted(os.listdir(class_dirs[class_name])):
            if filename.lower().endswith(".tif"):
                samples.append(
                    (os.path.join(class_dirs[class_name], filename),
                     CLASS_NAMES.index(class_name))
                )
    return samples


class EuroSATMultispectral(Dataset):
    def __init__(self, samples, indices, mean, std, augment=False):
        self.samples = samples
        self.indices = indices
        self.mean = torch.tensor(mean, dtype=torch.float32).view(13, 1, 1)
        self.std = torch.tensor(std, dtype=torch.float32).view(13, 1, 1)
        self.augment = augment

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        sample_index = self.indices[item]
        path, label = self.samples[sample_index]
        with rasterio.open(path) as source:
            image = source.read().astype(np.float32) / 10000.0

        image = torch.from_numpy(image)
        if self.augment:
            if torch.rand(()) < 0.5:
                image = torch.flip(image, dims=[2])
            if torch.rand(()) < 0.5:
                image = torch.flip(image, dims=[1])
            image = torch.rot90(image, int(torch.randint(0, 4, (1,))), dims=[1, 2])

        image = (image - self.mean) / self.std
        return image, label


def calculate_band_statistics(samples, indices):
    """Calculate training-only normalization statistics without leaking test data."""
    sums = np.zeros(13, dtype=np.float64)
    squared_sums = np.zeros(13, dtype=np.float64)
    pixel_count = 0

    print("Calculating training-band normalization statistics...")
    for position, sample_index in enumerate(indices, start=1):
        path, _ = samples[sample_index]
        with rasterio.open(path) as source:
            image = source.read().astype(np.float32) / 10000.0
        pixels = image.reshape(13, -1).astype(np.float64)
        sums += pixels.sum(axis=1)
        squared_sums += np.square(pixels).sum(axis=1)
        pixel_count += pixels.shape[1]
        if position % 1000 == 0:
            print(f"  processed {position}/{len(indices)} training images")

    mean = sums / pixel_count
    variance = np.maximum(squared_sums / pixel_count - np.square(mean), 1e-6)
    std = np.sqrt(variance)
    return mean.tolist(), std.tolist()


def build_model(num_classes, pretrained):
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = resnet18(weights=weights)

    old_conv = model.conv1
    new_conv = nn.Conv2d(
        13,
        old_conv.out_channels,
        kernel_size=old_conv.kernel_size,
        stride=old_conv.stride,
        padding=old_conv.padding,
        bias=False,
    )
    with torch.no_grad():
        if pretrained:
            new_conv.weight.copy_(
                old_conv.weight.mean(dim=1, keepdim=True).repeat(1, 13, 1, 1)
            )
            # Preserve the ImageNet RGB initialization for Sentinel-2 B04/B03/B02.
            new_conv.weight[:, 3] = old_conv.weight[:, 0]  # B04, red
            new_conv.weight[:, 2] = old_conv.weight[:, 1]  # B03, green
            new_conv.weight[:, 1] = old_conv.weight[:, 2]  # B02, blue
    model.conv1 = new_conv
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def run_epoch(model, loader, criterion, optimizer, scaler, device, train):
    model.train(train)
    total_loss = 0.0
    correct = 0
    total = 0
    autocast = (
        torch.autocast(device_type="cuda", dtype=torch.float16)
        if device.type == "cuda"
        else nullcontext()
    )

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        if train:
            optimizer.zero_grad(set_to_none=True)

        with autocast:
            logits = model(images)
            loss = criterion(logits, labels)

        if train:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


def predict(model, loader, device):
    model.eval()
    predictions, labels = [], []
    with torch.no_grad():
        for images, batch_labels in loader:
            logits = model(images.to(device, non_blocking=True))
            predictions.extend(logits.argmax(dim=1).cpu().numpy())
            labels.extend(batch_labels.numpy())
    return np.asarray(labels), np.asarray(predictions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-pretrained", action="store_true")
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    samples = find_samples()
    with open(SPLITS_PATH, encoding="utf-8") as file:
        splits = json.load(file)
    max_index = max(max(values) for values in splits.values())
    if max_index >= len(samples):
        raise RuntimeError(
            f"splits.json references index {max_index}, but only {len(samples)} "
            "multispectral samples were found."
        )

    mean, std = calculate_band_statistics(samples, splits["train"])
    train_set = EuroSATMultispectral(samples, splits["train"], mean, std, augment=True)
    val_set = EuroSATMultispectral(samples, splits["val"], mean, std)
    test_set = EuroSATMultispectral(samples, splits["test"], mean, std)

    loader_args = {
        "batch_size": args.batch_size,
        "num_workers": args.workers,
        "pin_memory": device.type == "cuda",
    }
    train_loader = DataLoader(train_set, shuffle=True, **loader_args)
    val_loader = DataLoader(val_set, shuffle=False, **loader_args)
    test_loader = DataLoader(test_set, shuffle=False, **loader_args)

    model = build_model(len(CLASS_NAMES), not args.no_pretrained).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    best_val_accuracy = -1.0
    best_epoch = 0
    epochs_without_improvement = 0
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        train_loss, train_accuracy = run_epoch(
            model, train_loader, criterion, optimizer, scaler, device, train=True
        )
        val_loss, val_accuracy = run_epoch(
            model, val_loader, criterion, optimizer, scaler, device, train=False
        )
        scheduler.step()
        print(
            f"Epoch {epoch:02d}/{args.epochs} | "
            f"train loss {train_loss:.4f}, acc {train_accuracy:.4f} | "
            f"val loss {val_loss:.4f}, acc {val_accuracy:.4f}"
        )

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            best_epoch = epoch
            epochs_without_improvement = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "mean": mean,
                    "std": std,
                    "classes": CLASS_NAMES,
                    "model": "resnet18",
                    "epoch": epoch,
                    "val_accuracy": val_accuracy,
                },
                CHECKPOINT_PATH,
            )
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"Early stopping after epoch {epoch}.")
                break

    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    y_true, y_pred = predict(model, test_loader, device)
    report = classification_report(y_true, y_pred, target_names=CLASS_NAMES)
    matrix = confusion_matrix(y_true, y_pred)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("Model: multispectral resnet18\n")
        file.write("Input: all 13 Sentinel-2 bands, spatial structure preserved\n")
        file.write(f"Best epoch: {best_epoch}\n")
        file.write(f"Validation accuracy: {best_val_accuracy:.4f}\n\n")
        file.write(report)
        file.write("\n\nConfusion Matrix:\n")
        file.write(str(matrix))
        file.write("\n\nBand normalization mean:\n")
        file.write(str(mean))
        file.write("\nBand normalization std:\n")
        file.write(str(std))

    print(f"\nTest report saved to {REPORT_PATH}")
    print(f"Best checkpoint saved to {CHECKPOINT_PATH}")
    print(report)


if __name__ == "__main__":
    main()
