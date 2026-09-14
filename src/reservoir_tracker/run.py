import os
import sys

sys.path.append(os.path.abspath("."))

from src.reservoir_tracker.depletion_tracker import analyze_depletion

def main():
    t0_image = "src/reservoir_tracker/data/t0_spring.tif"
    t1_image = "src/reservoir_tracker/data/t1_summer.tif"
    ckpt = "checkpoints/resnet50_m3_best.pth"

    analyze_depletion(t0_image, t1_image, ckpt)

if __name__ == "__main__":
    main()