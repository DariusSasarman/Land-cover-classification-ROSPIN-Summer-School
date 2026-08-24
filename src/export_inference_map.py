import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button
import os

# 1. EuroSAT class names and representative color palette
CLASSES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway", "Industrial",
    "Pasture", "PermanentCrop", "Residential", "River", "SeaLake"
]

CLASS_COLORS = [
    "#F0E68C",  # AnnualCrop
    "#228B22",  # Forest
    "#32CD32",  # HerbaceousVegetation
    "#696969",  # Highway
    "#FF0000",  # Industrial
    "#98FB98",  # Pasture
    "#D2B48C",  # PermanentCrop
    "#FF69B4",  # Residential
    "#00BFFF",  # River
    "#0000CD",  # SeaLake
]

# 2. Load predictions, positions, and RGB patches
predictions = np.load("data/processed/tiles/predictions.npy")
positions = np.load("data/processed/tiles/positions.npy")
patches_rgb = np.load("data/processed/tiles/patches_rgb.npy")
patches_rgb = np.transpose(patches_rgb, (0, 2, 3, 1))



print(f"Total tiles evaluated: {len(predictions)}")

# 3. Print class distribution statistics
print("\n--- Land Cover Statistics for Cluj AOI ---")
unique, counts = np.unique(predictions, return_counts=True)
for u, c in zip(unique, counts):
    pct = (c / len(predictions)) * 100
    print(f"{CLASSES[u]:<22}: {c:4d} patches ({pct:5.1f}%)")

# 4. Reconstruct the 2D prediction grid
n_rows = positions[:, 0].max() + 1
n_cols = positions[:, 1].max() + 1

grid_2d = np.zeros((n_rows, n_cols), dtype=np.int32)
for (r, c), pred in zip(positions, predictions):
    grid_2d[r, c] = pred

# 5. Reconstruct RGB mosaic from patches
tile_h, tile_w = patches_rgb.shape[1:3]

rgb_mosaic = np.zeros((n_rows * tile_h, n_cols * tile_w, 3), dtype=patches_rgb.dtype)
for (r, c), patch in zip(positions, patches_rgb):
    rgb_mosaic[r*tile_h:(r+1)*tile_h, c*tile_w:(c+1)*tile_w] = patch

# Normalize to [0,1] float if not uint8
if rgb_mosaic.dtype != np.uint8:
    rgb_mosaic = rgb_mosaic.astype(np.float32)
    rgb_mosaic = (rgb_mosaic - rgb_mosaic.min()) / (rgb_mosaic.max() - rgb_mosaic.min() + 1e-8)

# 6. Upscale prediction grid to pixel resolution to align with RGB mosaic
grid_2d_upscaled = np.repeat(np.repeat(grid_2d, tile_h, axis=0), tile_w, axis=1)

# 7. Build colormap for classification overlay
cmap = plt.matplotlib.colors.ListedColormap(CLASS_COLORS)
norm = plt.matplotlib.colors.BoundaryNorm(range(len(CLASSES) + 1), cmap.N)

# 8. Plot RGB base + classification overlay
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(
    left=0.05,
    right=0.78,   # leave room for legend on the right
    top=0.92,
    bottom=0.2    # leave room for slider/button
)

ax.imshow(rgb_mosaic)
overlay = ax.imshow(grid_2d_upscaled, cmap=cmap, norm=norm, alpha=0.5)
ax.set_title(f"Cluj AOI - Land Cover Overlay ({n_rows}x{n_cols} tiles)")
ax.axis("off")

legend_patches = [
    mpatches.Patch(color=CLASS_COLORS[i], label=CLASSES[i])
    for i in range(len(CLASSES)) if i in unique
]
ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)

# 9. Transparency slider
ax_slider = plt.axes([0.25, 0.08, 0.5, 0.03])
alpha_slider = Slider(ax_slider, "Overlay Opacity", 0.0, 1.0, valinit=0.5)

def update(val):
    overlay.set_alpha(alpha_slider.val)
    fig.canvas.draw_idle()

alpha_slider.on_changed(update)

# 10. Save button
ax_button = plt.axes([0.82, 0.08, 0.1, 0.04])
save_button = Button(ax_button, "Save")

def save(event):
    elements = [ax_button,ax_slider]
    for element in elements :
        element.set_visible(False)
    os.makedirs("data/processed/maps", exist_ok=True)
    fig.savefig("data/processed/maps/overlay_map.png", dpi=300, bbox_inches="tight")
    print("Saved to data/processed/maps/overlay_map.png")
    for element in elements :
        element.set_visible(True)
save_button.on_clicked(save)

plt.show()
