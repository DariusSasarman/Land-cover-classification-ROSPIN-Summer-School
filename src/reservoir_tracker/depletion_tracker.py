import os
import sys
import rasterio
import numpy as np
import torch
from torchvision import transforms
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Base directory for this tracker module
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PATCH_SIZE = 64
PIXEL_RES_M = 10.0  # Sentinel-2 10m bands

def read_multispectral_data(tif_path):
    with rasterio.open(tif_path) as src:
        arr = src.read().astype(np.float32)
        h, w = src.height, src.width

    # Handle Sentinel-2 scaling if values are 0-10000 integers
    if np.nanmax(arr) > 10.0:
        arr = arr / 10000.0

    # Bands: 0:B02(Blue), 1:B03(Green), 2:B04(Red), 3:B08(NIR), 4:B11, 5:B12
    green = arr[1]
    nir = arr[3]
    
    # NDWI calculation with eps to avoid divide-by-zero
    ndwi = (green - nir) / (green + nir + 1e-6)

    # Clean out nodata/blank borders if any
    nodata_mask = (green == 0) & (nir == 0)
    ndwi[nodata_mask] = -1.0

    # Diagnostic check on NDWI ranges
    print(f"[{os.path.basename(tif_path)}] NDWI min: {np.nanmin(ndwi):.3f}, max: {np.nanmax(ndwi):.3f}, mean: {np.nanmean(ndwi):.3f}")

    n_rows = h // PATCH_SIZE
    n_cols = w // PATCH_SIZE
    patches = []
    positions = []

    for r in range(n_rows):
        for c in range(n_cols):
            patch_rgb = arr[[2, 1, 0], r*PATCH_SIZE:(r+1)*PATCH_SIZE, c*PATCH_SIZE:(c+1)*PATCH_SIZE]
            patches.append(patch_rgb)
            positions.append((r, c))

    return arr, ndwi, np.stack(patches), np.array(positions), (n_rows, n_cols)

def predict_patches(patches, model):
    p98 = np.percentile(patches, 98)
    norm = np.clip(patches / (p98 + 1e-6), 0, 1)
    
    tensor_data = torch.tensor(norm).float()
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    tensor_data = normalize(tensor_data)

    preds = []
    with torch.no_grad():
        for i in range(0, len(tensor_data), 32):
            batch = tensor_data[i : i + 32].to(DEVICE)
            preds.extend(model(batch).argmax(dim=1).cpu().numpy())
    return np.array(preds)

def analyze_depletion(t0_path, t1_path, checkpoint_path):
    output_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Model Loader
    from src.models import get_resnet_model
    variant = "resnet50" if "50" in checkpoint_path else "resnet18"
    
    model = get_resnet_model(
        model_variant=variant,
        num_classes=10,
        use_architectural_mod=False,
        stem_conv="pretrained"
    )
    
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    else:
        state_dict = checkpoint

    cleaned_state_dict = {}
    for k, v in state_dict.items():
        new_key = k
        if new_key.startswith("module."):
            new_key = new_key[7:]
        if new_key.startswith("model."):
            new_key = new_key[6:]
        cleaned_state_dict[new_key] = v

    res = model.load_state_dict(cleaned_state_dict, strict=False)
    print(f"Model loaded: {variant}. Missing keys: {len(res.missing_keys)}, Unexpected keys: {len(res.unexpected_keys)}")
    model.to(DEVICE)
    model.eval()

    # 2. Extract Data
    print("Extracting T0 (Spring Baseline)...")
    _, ndwi_t0, patches_t0, positions, (n_rows, n_cols) = read_multispectral_data(t0_path)
    print("Extracting T1 (Summer / Depleted)...")
    _, ndwi_t1, patches_t1, _, _ = read_multispectral_data(t1_path)

    # 3. Model Inference (Water classes in EuroSAT: 8=River, 9=SeaLake)
    preds_t0 = predict_patches(patches_t0, model)
    preds_t1 = predict_patches(patches_t1, model)
    
    # 4. Pixel-level NDWI Water Masks
    # We use a threshold of -0.05 to capture deep clear reservoir water without getting cut off
    WATER_THRESHOLD = 0.0
    pixel_water_t0 = ndwi_t0 > WATER_THRESHOLD
    pixel_water_t1 = ndwi_t1 > WATER_THRESHOLD

    # 5. Quantify Surface Area
    pixel_area_km2 = (PIXEL_RES_M ** 2) / 1e6
    area_t0_km2 = np.sum(pixel_water_t0) * pixel_area_km2
    area_t1_km2 = np.sum(pixel_water_t1) * pixel_area_km2
    loss_km2 = area_t0_km2 - area_t1_km2
    pct_loss = (loss_km2 / (area_t0_km2 + 1e-6)) * 100

    print("\n" + "="*50)
    print("       RESERVOIR DEPLETION ANALYSIS REPORT")
    print("="*50)
    print(f"High-Water (T0) Area : {area_t0_km2:.3f} km² ({np.sum(pixel_water_t0)} pixels)")
    print(f"Low-Water (T1) Area  : {area_t1_km2:.3f} km² ({np.sum(pixel_water_t1)} pixels)")
    print(f"Net Surface Loss     : {loss_km2:.3f} km² ({pct_loss:.2f}% reduction)")
    print("="*50 + "\n")

    # 6. Save Transition Map
    change_map = np.zeros(pixel_water_t0.shape, dtype=np.uint8)
    change_map[pixel_water_t0 & pixel_water_t1] = 1   # Stable Water
    change_map[pixel_water_t0 & ~pixel_water_t1] = 2  # Receded / Depleted
    change_map[~pixel_water_t0 & pixel_water_t1] = 3  # Expanded Water

    colors = ["#e8e8e8", "#1f77b4", "#d62728", "#2ca02c"]
    cmap = plt.matplotlib.colors.ListedColormap(colors)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(change_map, cmap=cmap, vmin=0, vmax=3)
    ax.set_title(f"Tarnița Reservoir Surface Dynamics\nT0 Water: {area_t0_km2:.2f} km² | T1 Water: {area_t1_km2:.2f} km²")
    ax.axis("off")

    legend_elements = [
        mpatches.Patch(color="#e8e8e8", label="Surrounding Land"),
        mpatches.Patch(color="#1f77b4", label="Permanent / Stable Water"),
        mpatches.Patch(color="#d62728", label="Depleted Surface (Lost)"),
        mpatches.Patch(color="#2ca02c", label="Expanded Water Surface")
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    out_png = os.path.join(output_dir, "depletion_map.png")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved visualization to: {out_png}")