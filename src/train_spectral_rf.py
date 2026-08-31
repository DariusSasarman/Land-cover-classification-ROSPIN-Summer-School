"""
Second Random Forest baseline, this time trained on Sentinel-2 spectral
bands instead of RGB.

Mirrors train_baseline_rf.py (same splits.json, same RF hyperparameters,
same mean/std/min/max feature-extraction pattern) so the two reports are
a fair apples-to-apples comparison - the only thing that changes is which
channels feed the model:

  baseline_rf_report.txt  -> R, G, B                       (12 features)
  spectral_rf_report.txt  -> B08, B11, B12 + 6 derived      (36 features)
                              indices computed from them

Run download_eurosat_allbands.py first to fetch the 13-band imagery.
"""

import json
import os
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_ROOT = os.path.join(REPO_ROOT, "reports")
os.makedirs(REPORTS_ROOT, exist_ok=True)

ALLBANDS_ROOT = os.path.join(REPO_ROOT, "data", "raw", "EuroSATallBands")

# Standard Sentinel-2 L1C band order used by the EuroSAT all-bands GeoTIFFs.
BAND_ORDER = ["B01", "B02", "B03", "B04", "B05", "B06", "B07",
              "B08", "B08A", "B09", "B10", "B11", "B12"]

KNOWN_CLASSES = ["AnnualCrop", "Forest", "HerbaceousVegetation", "Highway",
                  "Industrial", "Pasture", "PermanentCrop", "Residential",
                  "River", "SeaLake"]

EPS = 1e-6  # avoids divide-by-zero in the ratio/index features


def find_class_dirs(root):
    """Locate the 10 class folders no matter how the zip was nested."""
    class_dirs = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        name = os.path.basename(dirpath)
        if name in KNOWN_CLASSES and any(f.lower().endswith(".tif") for f in filenames):
            class_dirs[name] = dirpath
    missing = set(KNOWN_CLASSES) - set(class_dirs)
    if missing:
        raise FileNotFoundError(
            f"Could not find class folders {sorted(missing)} under '{root}'. "
            "Run download_eurosat_allbands.py first."
        )
    return class_dirs


class EuroSATAllBands:
    """
    Minimal 13-band EuroSAT loader.

    Class/file ordering intentionally mirrors what
    torchvision.datasets.EuroSAT (the RGB version used everywhere else in
    this repo) does internally: classes sorted alphabetically, files within
    each class sorted alphabetically. That's what lets index i here refer
    to the same underlying patch as index i in the RGB dataset, so the
    existing data/processed/splits.json can be reused as-is.

    Worth a quick sanity check the first time you run this: open the same
    index in both datasets and confirm the RGB preview looks like the same
    scene as the tif's B04/B03/B02 bands.
    """

    def __init__(self, root):
        class_dirs = find_class_dirs(root)
        self.classes = sorted(class_dirs)
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        self.samples = []
        for c in self.classes:
            for fname in sorted(os.listdir(class_dirs[c])):
                if fname.lower().endswith(".tif"):
                    self.samples.append((os.path.join(class_dirs[c], fname), self.class_to_idx[c]))

    def __len__(self):
        return len(self.samples)

    def read_bands(self, idx):
        path, label = self.samples[idx]
        with rasterio.open(path) as src:
            arr = src.read().astype(np.float32)  # shape: (13, H, W)
        return arr, label


def spectral_channels(arr13):
    """B08/B11/B12 plus 6 functions of them: 3 normalized-difference-style
    indices and 3 simple ratios. All are computable from just these three
    bands (no red/blue needed)."""
    b8 = arr13[BAND_ORDER.index("B08")]
    b11 = arr13[BAND_ORDER.index("B11")]
    b12 = arr13[BAND_ORDER.index("B12")]

    ndmi = (b8 - b11) / (b8 + b11 + EPS)        # moisture content (canopy/soil)
    nbr = (b8 - b12) / (b8 + b12 + EPS)         # burn / moisture-stress ratio
    swir_diff = (b11 - b12) / (b11 + b12 + EPS)  # SWIR1 vs SWIR2 contrast
    r_8_11 = b8 / (b11 + EPS)
    r_8_12 = b8 / (b12 + EPS)
    r_11_12 = b11 / (b12 + EPS)

    return {
        "B08": b8, "B11": b11, "B12": b12,
        "NDMI": ndmi, "NBR": nbr, "SWIR_DIFF": swir_diff,
        "R_B8_B11": r_8_11, "R_B8_B12": r_8_12, "R_B11_B12": r_11_12,
    }


def extract_spectral_stats(arr13):
    feats, names = [], []
    for cname, band in spectral_channels(arr13).items():
        feats.extend([band.mean(), band.std(), band.min(), band.max()])
        names.extend([f"{cname}_mean", f"{cname}_std", f"{cname}_min", f"{cname}_max"])
    return feats, names


print("Loading EuroSAT multispectral (13-band) dataset...")
dataset = EuroSATAllBands(ALLBANDS_ROOT)
print(f"Found {len(dataset)} images across {len(dataset.classes)} classes: {dataset.classes}")

with open(os.path.join(REPO_ROOT, "data", "processed", "splits.json")) as f:
    splits = json.load(f)

max_idx = max(max(splits["train"]), max(splits["val"]), max(splits["test"]))
if max_idx >= len(dataset):
    raise RuntimeError(
        f"splits.json references index {max_idx}, but the multispectral "
        f"dataset only has {len(dataset)} images. The all-bands dataset "
        "isn't lining up 1:1 with the RGB one splits.json was built from - "
        "double check the download/extraction."
    )

feature_names = None


def build_xy(indices):
    global feature_names
    X, y = [], []
    for i in indices:
        arr13, label = dataset.read_bands(i)
        feats, names = extract_spectral_stats(arr13)
        if feature_names is None:
            feature_names = names
        X.append(feats)
        y.append(label)
    return X, y


print("Extracting spectral features (B08, B11, B12 + derived indices) from train set...")
X_train, y_train = build_xy(splits["train"])

print("Extracting spectral features from test set...")
X_test, y_test = build_xy(splits["test"])

print("Training Random Forest on spectral feature set...")
clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

report = classification_report(y_test, y_pred, target_names=dataset.classes)
cm = confusion_matrix(y_test, y_pred)

print(report)
print(cm)

top_features = sorted(zip(feature_names, clf.feature_importances_), key=lambda x: -x[1])[:10]

report_path = os.path.join(REPORTS_ROOT, "spectral_rf_report.txt")
with open(report_path, "w") as f:
    f.write(report)
    f.write("\n\nConfusion Matrix:\n")
    f.write(str(cm))
    f.write("\n\nTop 10 most important features:\n")
    for name, imp in top_features:
        f.write(f"{name}: {imp:.4f}\n")

print(f"Report saved to {report_path}")
