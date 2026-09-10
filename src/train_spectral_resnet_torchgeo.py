"""Train a Sentinel-2 multispectral ResNet-18 on the 13-band EuroSAT dataset.

This version uses TorchGeo's Sentinel-2 pretrained ResNet-18:
    ResNet18_Weights.SENTINEL2_ALL_MOCO

The pretrained checkpoint is downloaded automatically by TorchGeo on first run.
The dataset keeps all 13 Sentinel-2 bands and the existing train/val/test splits.

Expected band order in the EuroSAT GeoTIFF:
    B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B10, B11, B12
"""

import argparse
import json
import os
import random
from contextlib import nullcontext

import numpy as np
import rasterio
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader, Dataset
from torchgeo.models import ResNet18_Weights


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLBANDS_ROOT = os.path.join(REPO_ROOT, "data", "raw", "EuroSATallBands")
SPLITS_PATH = os.path.join(REPO_ROOT, "data", "processed", "splits.json")
REPORT_PATH = os.path.join(
    REPO_ROOT, "reports", "spectral_resnet_torchgeo_report.txt"
)
CHECKPOINT_PATH = os.path.join(
    REPO_ROOT, "checkpoints", "spectral_resnet_torchgeo_best.pth"
)

# IMPORTANT:
# This is the Sentinel-2 order used by TorchGeo/SSL4EO-S12 for the
# SENTINEL2_ALL_MOCO weights.
BAND_ORDER = [
    "B01", "B02", "B03", "B04", "B05", "B06", "B07",
    "B08", "B8A", "B09", "B10", "B11", "B12",
]

CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway",
    "Industrial", "Pasture", "PermanentCrop", "Residential",
    "River", "SeaLake",
]

NUM_BANDS = 13

# The SSL4EO-S12 MoCo weights were trained using Sentinel-2 values divided
# by 10000. We therefore DO NOT calculate a new dataset mean/std here.
# This is deliberate: the pretrained representation expects the 10k scaling.
INPUT_SIZE = 224


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
                    (
                        os.path.join(class_dirs[class_name], filename),
                        CLASS_NAMES.index(class_name),
                    )
                )

    return samples


class EuroSATMultispectral(Dataset):
    def __init__(self, samples, indices, augment=False):
        self.samples = samples
        self.indices = indices
        self.augment = augment

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        sample_index = self.indices[item]
        path, label = self.samples[sample_index]

        with rasterio.open(path) as source:
            image = source.read().astype(np.float32)

        if image.shape[0] != NUM_BANDS:
            raise RuntimeError(
                f"{path} contains {image.shape[0]} bands, "
                f"but {NUM_BANDS} are required."
            )

        # EuroSAT all-bands values are stored as Sentinel-2 reflectance
        # scaled by 10000. This matches the preprocessing used by the
        # SSL4EO-S12 Sentinel-2 MoCo weights.
        image = torch.from_numpy(image) / 10000.0

        if self.augment:
            if torch.rand(()) < 0.5:
                image = torch.flip(image, dims=[2])

            if torch.rand(()) < 0.5:
                image = torch.flip(image, dims=[1])

            image = torch.rot90(
                image,
                int(torch.randint(0, 4, (1,))),
                dims=[1, 2],
            )

        # TorchGeo's pretrained ResNet-18 uses 224x224 crops.
        # EuroSAT patches are 64x64, so resize them to the expected
        # spatial input size before the network.
        image = F.interpolate(
            image.unsqueeze(0),
            size=(INPUT_SIZE, INPUT_SIZE),
            mode="bilinear",
            align_corners=False,
        ).squeeze(0)

        return image, label


def load_local_weights(model, weights_path):
    """Load either a raw state dict or a training checkpoint."""

    checkpoint = torch.load(
        weights_path,
        map_location="cpu",
        weights_only=False,
    )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    elif isinstance(checkpoint, dict):
        state_dict = checkpoint
    else:
        raise RuntimeError(
            f"Unsupported checkpoint format in {weights_path}. "
            "Expected a state dict or a dictionary containing "
            "'model_state_dict'."
        )

    incompatible = model.load_state_dict(
        state_dict,
        strict=False,
    )

    print(f"Local weights loaded from {weights_path}")
    print(f"Missing keys: {incompatible.missing_keys}")
    print(f"Unexpected keys: {incompatible.unexpected_keys}")


def build_model(num_classes, pretrained=True, weights_path=None):
    """Build ResNet-18 with TorchGeo Sentinel-2 pretrained weights."""

    if pretrained:
        model = timm.create_model(
            "resnet18",
            in_chans=NUM_BANDS,
            num_classes=num_classes,
        )

        if weights_path:
            load_local_weights(model, weights_path)
        else:
            weights = ResNet18_Weights.SENTINEL2_ALL_MOCO

            print("Loading TorchGeo Sentinel-2 pretrained weights...")
            print(f"Dataset: {weights.meta.get('dataset')}")
            print(f"SSL method: {weights.meta.get('ssl_method')}")
            print(f"Input channels: {weights.meta['in_chans']}")
            print(f"Bands: {weights.meta.get('bands')}")

            # Make sure the checkpoint really is the 13-band Sentinel-2 model.
            if weights.meta["in_chans"] != NUM_BANDS:
                raise RuntimeError(
                    f"TorchGeo checkpoint expects {weights.meta['in_chans']} "
                    f"channels, but this script uses {NUM_BANDS}."
                )

            state_dict = weights.get_state_dict(
                progress=True,
                check_hash=True,
                weights_only=True,
            )

            # strict=False is required because the pretrained classifier is not
            # the final 10-class EuroSAT classifier.
            incompatible = model.load_state_dict(
                state_dict,
                strict=False,
            )

            print("Pretrained weights loaded.")
            print(f"Missing keys: {incompatible.missing_keys}")
            print(f"Unexpected keys: {incompatible.unexpected_keys}")

    else:
        print("Building a 13-band ResNet-18 from scratch.")

        model = timm.create_model(
            "resnet18",
            in_chans=NUM_BANDS,
            num_classes=num_classes,
        )

    return model


def run_epoch(
    model,
    loader,
    criterion,
    optimizer,
    scaler,
    device,
    train,
):
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

    predictions = []
    labels = []

    with torch.no_grad():
        for images, batch_labels in loader:
            logits = model(images.to(device, non_blocking=True))

            predictions.extend(
                logits.argmax(dim=1).cpu().numpy()
            )
            labels.extend(batch_labels.numpy())

    return np.asarray(labels), np.asarray(predictions)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help=(
            "Path to a local 13-band ResNet-18 .pth file. "
            "If omitted, download TorchGeo weights automatically."
        ),
    )

    parser.add_argument(
        "--no-pretrained",
        action="store_true",
        help="Train a 13-band ResNet-18 from scratch instead of using TorchGeo.",
    )

    args = parser.parse_args()

    set_seed(args.seed)

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Using device: {device}")
    print(f"Input size: {INPUT_SIZE}x{INPUT_SIZE}")
    print(f"Bands: {BAND_ORDER}")

    samples = find_samples()

    with open(SPLITS_PATH, encoding="utf-8") as file:
        splits = json.load(file)

    max_index = max(
        max(values) for values in splits.values()
    )

    if max_index >= len(samples):
        raise RuntimeError(
            f"splits.json references index {max_index}, "
            f"but only {len(samples)} multispectral samples were found."
        )

    train_set = EuroSATMultispectral(
        samples,
        splits["train"],
        augment=True,
    )

    val_set = EuroSATMultispectral(
        samples,
        splits["val"],
        augment=False,
    )

    test_set = EuroSATMultispectral(
        samples,
        splits["test"],
        augment=False,
    )

    loader_args = {
        "batch_size": args.batch_size,
        "num_workers": args.workers,
        "pin_memory": device.type == "cuda",
    }

    train_loader = DataLoader(
        train_set,
        shuffle=True,
        **loader_args,
    )

    val_loader = DataLoader(
        val_set,
        shuffle=False,
        **loader_args,
    )

    test_loader = DataLoader(
        test_set,
        shuffle=False,
        **loader_args,
    )

    model = build_model(
        num_classes=len(CLASS_NAMES),
        pretrained=not args.no_pretrained,
        weights_path=args.weights,
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        label_smoothing=0.1
    )

    # Lower LR is appropriate for fine-tuning pretrained features.
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-4 if not args.no_pretrained else 3e-4,
        weight_decay=1e-4,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=args.epochs,
    )

    scaler = torch.amp.GradScaler(
        "cuda",
        enabled=device.type == "cuda",
    )

    best_val_accuracy = -1.0
    best_epoch = 0
    epochs_without_improvement = 0

    os.makedirs(
        os.path.dirname(CHECKPOINT_PATH),
        exist_ok=True,
    )

    for epoch in range(1, args.epochs + 1):
        train_loss, train_accuracy = run_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            scaler,
            device,
            train=True,
        )

        val_loss, val_accuracy = run_epoch(
            model,
            val_loader,
            criterion,
            optimizer,
            scaler,
            device,
            train=False,
        )

        scheduler.step()

        print(
            f"Epoch {epoch:02d}/{args.epochs} | "
            f"train loss {train_loss:.4f}, "
            f"acc {train_accuracy:.4f} | "
            f"val loss {val_loss:.4f}, "
            f"acc {val_accuracy:.4f}"
        )

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            best_epoch = epoch
            epochs_without_improvement = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": CLASS_NAMES,
                    "bands": BAND_ORDER,
                    "model": "resnet18",
                    "pretrained": not args.no_pretrained,
                    "pretrained_weights": (
                        "SENTINEL2_ALL_MOCO"
                        if not args.no_pretrained
                        else None
                    ),
                    "input_size": INPUT_SIZE,
                    "epoch": epoch,
                    "val_accuracy": val_accuracy,
                },
                CHECKPOINT_PATH,
            )

            print(
                f"  -> New best model saved "
                f"(val acc={val_accuracy:.4f})"
            )

        else:
            epochs_without_improvement += 1

            if epochs_without_improvement >= args.patience:
                print(
                    f"Early stopping after epoch {epoch}."
                )
                break

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    y_true, y_pred = predict(
        model,
        test_loader,
        device,
    )

    report = classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
    )

    os.makedirs(
        os.path.dirname(REPORT_PATH),
        exist_ok=True,
    )

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "Model: TorchGeo Sentinel-2 ResNet-18\n"
        )
        file.write(
            "Pretraining: SENTINEL2_ALL_MOCO\n"
        )
        file.write(
            "Dataset: SSL4EO-S12\n"
        )
        file.write(
            "Input: all 13 Sentinel-2 bands\n"
        )
        file.write(
            "Band order: "
            + str(BAND_ORDER)
            + "\n"
        )
        file.write(
            "Input scaling: divide by 10000\n"
        )
        file.write(
            f"Input size: {INPUT_SIZE}x{INPUT_SIZE}\n"
        )
        file.write(
            f"Best epoch: {best_epoch}\n"
        )
        file.write(
            f"Validation accuracy: "
            f"{best_val_accuracy:.4f}\n\n"
        )

        file.write(report)

        file.write(
            "\n\nConfusion Matrix:\n"
        )
        file.write(str(matrix))

    print(
        f"\nTest report saved to {REPORT_PATH}"
    )

    print(
        f"Best checkpoint saved to "
        f"{CHECKPOINT_PATH}"
    )

    print(
        f"\nBest validation accuracy: "
        f"{best_val_accuracy:.4f}"
    )

    print("\nTest classification report:")
    print(report)

    print("\nConfusion Matrix:")
    print(matrix)


if __name__ == "__main__":
    main()
