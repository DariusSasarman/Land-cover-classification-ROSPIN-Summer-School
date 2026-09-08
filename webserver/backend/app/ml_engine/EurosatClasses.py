"""
Order of EuroSAT classes as output by the model's final linear layer.
Confirmed against the training notebook: torchvision.datasets.EuroSAT wraps
ImageFolder internally, which sorts class folder names alphabetically.
"""
from typing import List

EUROSAT_CLASS_ORDER: List[str] = [
    "AnnualCrop",
    "Forest",
    "HerbaceousVegetation",
    "Highway",
    "Industrial",
    "Pasture",
    "PermanentCrop",
    "Residential",
    "River",
    "SeaLake",
]