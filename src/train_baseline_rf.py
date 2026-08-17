import json
import os
import numpy as np
from torchvision.datasets import EuroSAT
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

os.makedirs("reports", exist_ok=True)

dataset = EuroSAT(root="data/raw", download=True)

with open("data/processed/splits.json") as f:
    splits = json.load(f)

def extract_band_stats(image):
    arr = np.array(image)
    stats = []
    for c in range(arr.shape[-1]):
        band = arr[:, :, c]
        stats.extend([band.mean(), band.std(), band.min(), band.max()])
    return stats

print("Extracting features from train set...")
X_train = [extract_band_stats(dataset[i][0]) for i in splits["train"]]
y_train = [dataset[i][1] for i in splits["train"]]

print("Extracting features from test set...")
X_test = [extract_band_stats(dataset[i][0]) for i in splits["test"]]
y_test = [dataset[i][1] for i in splits["test"]]

print("Training Random Forest...")
clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

report = classification_report(y_test, y_pred, target_names=dataset.classes)
cm = confusion_matrix(y_test, y_pred)

print(report)
print(cm)

with open("reports/baseline_rf_report.txt", "w") as f:
    f.write(report)
    f.write("\n\nConfusion Matrix:\n")
    f.write(str(cm))

print("Report saved to reports/baseline_rf_report.txt")