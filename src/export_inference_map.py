import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 1. EuroSAT class names and representative color palette
CLASSES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway", "Industrial",
    "Pasture", "PermanentCrop", "Residential", "River", "SeaLake"
]

# Color map matching standard land-cover conventions
CLASS_COLORS = [
    "#F0E68C",  # AnnualCrop (khaki)
    "#228B22",  # Forest (forest green)
    "#32CD32",  # HerbaceousVegetation (lime green)
    "#696969",  # Highway (dim gray)
    "#FF0000",  # Industrial (red)
    "#98FB98",  # Pasture (pale green)
    "#D2B48C",  # PermanentCrop (tan)
    "#FF69B4",  # Residential (hot pink)
    "#00BFFF",  # River (deep sky blue)
    "#0000CD",  # SeaLake (medium blue)
]

# 2. Load predictions and grid positions
predictions = np.load("data/processed/tiles/predictions.npy")
positions = np.load("data/processed/tiles/positions.npy")

print(f"Total tiles evaluated: {len(predictions)}")

# 3. Print Class Distribution Statistics
print("\n--- Land Cover Statistics for Cluj AOI ---")
unique, counts = np.unique(predictions, return_counts=True)
for u, c in zip(unique, counts):
    pct = (c / len(predictions)) * 100
    print(f"{CLASSES[u]:<22}: {c:4d} patches ({pct:5.1f}%)")

# 4. Reconstruct the 2D Prediction Grid
n_rows = positions[:, 0].max() + 1
n_cols = positions[:, 1].max() + 1

grid_2d = np.zeros((n_rows, n_cols), dtype=np.int32)
for (r, c), pred in zip(positions, predictions):
    grid_2d[r, c] = pred

# 5. Plot the Classification Map
cmap = plt.matplotlib.colors.ListedColormap(CLASS_COLORS)
norm = plt.matplotlib.colors.BoundaryNorm(range(len(CLASSES) + 1), cmap.N)

plt.figure(figsize=(14, 6))
im = plt.imshow(grid_2d, cmap=cmap, norm=norm)
plt.title(f"Cluj AOI - EuroSAT Land Cover Classification ({n_rows}x{n_cols} grid)", fontsize=14)
plt.axis("off")

# Add Legend
legend_patches = [
    mpatches.Patch(color=CLASS_COLORS[i], label=f"{CLASSES[i]}")
    for i in range(len(CLASSES)) if i in unique
]
plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)
plt.tight_layout()
plt.show()