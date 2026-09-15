# Land Cover Classification Model Overview

An end-to-end machine-learning pipeline for satellite land-cover classification and visual explainability on Sentinel-2 imagery.

This repository contains training, evaluation, and deployment code for several baseline and deep-learning models on the EuroSAT 10-class dataset.

---

## 1. Supported Models

| Model | Input / Bands | Accuracy | Macro F1 | Role | Evaluation Report | Weights / Checkpoint |
| :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| ResNet-18 (RGB) | 3 bands (RGB) | 97% | 0.97 | Production web model | [reports/resnet18_m3_report.txt](reports/resnet18_m3_report.txt) | [model/resnet18_m3_best.pth](model/resnet18_m3_best.pth) |
| Spectral ResNet-18 (TorchGeo) | 13 bands | 99% | 0.99 | High-accuracy benchmark | Benchmark report not included in this repository | [checkpoints/spectral_resnet_torchgeo_best.pth](checkpoints/spectral_resnet_torchgeo_best.pth) |
| ResNet-50 (RGB) | 3 bands (RGB) | 98% | 0.98 | Larger benchmark backbone | [reports/resnet50_report.txt](reports/resnet50_report.txt) | Not packaged in this repository |
| Spectral Random Forest | Spectral features | 87% | 0.86 | Traditional ML baseline | [reports/spectral_rf_report.txt](reports/spectral_rf_report.txt) | Not packaged in this repository |
| Baseline Random Forest | Basic features | 80% | 0.78 | Initial ML baseline | [reports/baseline_rf_report.txt](reports/baseline_rf_report.txt) | Not packaged in this repository |

> Note: The live web application uses the ResNet-18 RGB model because it offers the best balance between accuracy, inference speed, memory footprint, and ease of integration.

---

## 2. Model Selection for Web Deployment

The repository evaluated multiple architectures, but the live production system uses the RGB ResNet-18 model.

### Production choice: ResNet-18 (RGB)

- Accuracy: 97%
- Macro F1: 0.97
- Why it was chosen:
  - Fast inference
  - Low memory consumption
  - Good classification performance
  - Easy integration with the frontend/backend stack

### Why the other models were not used in production

- Spectral ResNet-18 (13-band): best benchmark accuracy (99%), but more demanding to integrate for live multi-band AOI processing and deployment.
- ResNet-50 (RGB): strong performance (98%), but heavier model size and higher resource overhead.
- Random forest baselines: lower accuracy (80%–87%) and weaker spatial feature learning for complex satellite scenes.

---

## 3. Evaluation Summary

### A. Production model: ResNet-18 (RGB)

- Accuracy: 97%
- Macro F1: 0.97
- Full report: [reports/resnet18_m3_report.txt](reports/resnet18_m3_report.txt)
- Model weights: [model/resnet18_m3_best.pth](model/resnet18_m3_best.pth)

Classification report:

```text
              precision    recall  f1-score   support

AnnualCrop       0.90      0.97      0.93       450
Forest           0.99      0.98      0.99       450
HerbaceousVegetation  0.96    0.98      0.97       450
Highway          0.98      0.98      0.98       375
Industrial       0.99      0.97      0.98       375
Pasture          0.99      0.88      0.93       300
PermanentCrop    0.95      0.94      0.94       375
Residential      0.97      1.00      0.98       450
River            0.97      0.97      0.97       375
SeaLake          1.00      0.97      0.99       450

            accuracy                           0.97      4050
           macro avg       0.97      0.96      0.97      4050
        weighted avg       0.97      0.97      0.97      4050
```

Confusion matrix:

```text
[[437   1   1   0   0   1   9   0   1   0]
 [  0 442   8   0   0   0   0   0   0   0]
 [  1   0 440   0   0   1   7   1   0   0]
 [  1   0   0 369   0   0   0   1   4   0]
 [  0   0   0   2 363   0   0  10   0   0]
 [ 23   3   4   1   0 264   2   0   3   0]
 [ 13   1   5   0   3   0 352   1   0   0]
 [  0   0   1   0   1   0   0 448   0   0]
 [  4   0   1   5   0   0   0   0 365   0]
 [  8   0   0   0   0   0   0   0   5 437]]
```

---

### B. Benchmark model: Spectral ResNet-18 (TorchGeo, 13-band)

- Accuracy: 99%
- Macro F1: 0.99
- Model checkpoint: [checkpoints/spectral_resnet_torchgeo_best.pth](checkpoints/spectral_resnet_torchgeo_best.pth)

Classification report (summary from benchmark training):

```text
              precision    recall  f1-score   support

AnnualCrop       0.99      0.99      0.99       450
Forest           1.00      1.00      1.00       450
HerbaceousVegetation  0.99    0.99      0.99       450
Highway          0.98      0.99      0.99       375
Industrial       0.99      0.99      0.99       375
Pasture          0.97      0.98      0.98       300
PermanentCrop    0.99      0.99      0.99       375
Residential      1.00      1.00      1.00       450
River            0.99      0.99      0.99       375
SeaLake          1.00      1.00      1.00       450

            accuracy                           0.99      4050
           macro avg       0.99      0.99      0.99      4050
        weighted avg       0.99      0.99      0.99      4050
```

Confusion matrix:

```text
[[445   0   0   0   0   2   3   0   0   0]
 [  0 449   1   0   0   0   0   0   0   0]
 [  1   0 445   0   0   3   1   0   0   0]
 [  0   0   0 373   0   1   1   0   0   0]
 [  0   0   0   3 371   0   0   1   0   0]
 [  2   0   2   0   0 295   0   0   1   0]
 [  2   0   2   1   0   0 370   0   0   0]
 [  0   0   0   0   2   0   0 448   0   0]
 [  0   0   0   2   0   2   0   0 371   0]
 [  0   0   0   0   0   0   0   0   1 449]]
```

---

### C. Benchmark model: ResNet-50 (RGB)

- Accuracy: 98%
- Macro F1: 0.98
- Full report: [reports/resnet50_report.txt](reports/resnet50_report.txt)

Classification report:

```text
              precision    recall  f1-score   support

AnnualCrop       0.97      0.97      0.97       450
Forest           0.99      1.00      0.99       450
HerbaceousVegetation  0.99    0.96      0.97       450
Highway          0.99      0.98      0.98       375
Industrial       0.99      0.99      0.99       375
Pasture          0.97      0.99      0.98       300
PermanentCrop    0.97      0.96      0.97       375
Residential      1.00      0.99      0.99       450
River            0.98      0.99      0.99       375
SeaLake          0.99      1.00      0.99       450

            accuracy                           0.98      4050
           macro avg       0.98      0.98      0.98      4050
        weighted avg       0.98      0.98      0.98      4050
```

Confusion matrix:

```text
[[438   0   0   1   0   1   7   0   1   2]
 [  0 450   0   0   0   0   0   0   0   0]
 [  4   4 430   1   0   6   4   0   0   1]
 [  0   0   0 368   0   1   0   0   6   0]
 [  0   0   0   1 372   0   0   2   0   0]
 [  1   0   0   0   0 297   0   0   0   2]
 [  8   0   4   0   1   0 361   0   1   0]
 [  0   0   0   1   4   0   0 445   0   0]
 [  0   1   0   1   0   0   0   0 373   0]
 [  1   0   0   0   0   0   0   0   1 448]]
```

---

### D. Baseline: Spectral Random Forest

- Accuracy: 87%
- Macro F1: 0.86
- Full report: [reports/spectral_rf_report.txt](reports/spectral_rf_report.txt)
- Top features: B12_mean, B12_std, R_B8_B12_std

Classification report:

```text
              precision    recall  f1-score   support

AnnualCrop       0.90      0.90      0.90       450
Forest           0.96      0.97      0.97       450
HerbaceousVegetation  0.89    0.91      0.90       450
Highway          0.69      0.59      0.64       375
Industrial       0.79      0.87      0.83       375
Pasture          0.83      0.84      0.84       300
PermanentCrop    0.81      0.80      0.80       375
Residential      0.86      0.85      0.86       450
River            0.90      0.95      0.92       375
SeaLake          1.00      0.99      0.99       450

            accuracy                           0.87      4050
           macro avg       0.86      0.87      0.86      4050
        weighted avg       0.87      0.87      0.87      4050
```

Confusion matrix:

```text
[[405   0   8  13   0   3  21   0   0   0]
 [  0 436   3   1   0   8   1   1   0   0]
 [  4   3 408   3   4   7  10   1   9   1]
 [  9   3  11 221  36  23  20  29  23   0]
 [  0   0   0  17 327   0   0  31   0   0]
 [  5   7   7  12   0 252  13   0   4   0]
 [ 27   2  14  24   2   6 299   0   1   0]
 [  0   0   3  15  44   1   4 383   0   0]
 [  0   1   2  12   3   2   0   0 355   0]
 [  0   0   2   0   0   1   0   0   2 445]]
```

---

### E. Baseline: Standard Random Forest

- Accuracy: 80%
- Macro F1: 0.78
- Full report: [reports/baseline_rf_report.txt](reports/baseline_rf_report.txt)

Classification report:

```text
              precision    recall  f1-score   support

AnnualCrop       0.82      0.84      0.83       450
Forest           0.92      0.96      0.94       450
HerbaceousVegetation  0.82    0.78      0.80       450
Highway          0.52      0.40      0.45       375
Industrial       0.88      0.90      0.89       375
Pasture          0.80      0.87      0.84       300
PermanentCrop    0.67      0.70      0.69       375
Residential      0.77      0.89      0.83       450
River            0.67      0.63      0.65       375
SeaLake          0.97      0.90      0.94       450

            accuracy                           0.80      4050
           macro avg       0.78      0.79      0.78      4050
        weighted avg       0.79      0.80      0.79      4050
```

Confusion matrix:

```text
[[379   2   4  12   0   6  28   0  15   4]
 [  0 434   0   0   0  13   0   0   2   1]
 [ 11   8 351  13   3   5  38  11   8   2]
 [ 30   0  15 151  20  13  33  54  59   0]
 [  0   0   3   4 339   0   2  24   3   0]
 [  3  11   5   3   0 262   4   3   8   1]
 [ 20   0  34  18   4  14 264  13   8   0]
 [  0   0   6  21  13   0   7 400   3   0]
 [ 16   4   4  68   8   8  15  12 237   3]
 [  2  15   4   2   0   6   3   0  13 405]]
```

---

## 4. Known Issues and Generalization Challenges

During testing on live Areas of Interest (AOIs), the Spectral ResNet-18 model showed domain-shift issues, including the misclassification of industrial regions as vegetation.

Key contributors:

1. Spectral channel and normalization mismatches between benchmark EuroSAT patches and real Sentinel-2 L2A tiles.
2. Mixed land-cover pixels in real urban and industrial areas.
3. Differences between cropped single-label EuroSAT samples and broader real-world AOI conditions.

These findings indicate that model performance remains excellent on benchmark data, but operational deployment still requires careful preprocessing and domain-aware validation for real AOI scenes.

---

## 5. Quick Links

- Project root: [README.md](README.md)
- Baseline RF report: [reports/baseline_rf_report.txt](reports/baseline_rf_report.txt)
- Spectral RF report: [reports/spectral_rf_report.txt](reports/spectral_rf_report.txt)
- ResNet-18 report: [reports/resnet18_m3_report.txt](reports/resnet18_m3_report.txt)
- ResNet-50 report: [reports/resnet50_report.txt](reports/resnet50_report.txt)
- Production model: [model/resnet18_m3_best.pth](model/resnet18_m3_best.pth)
- Benchmark checkpoint: [checkpoints/spectral_resnet_torchgeo_best.pth](checkpoints/spectral_resnet_torchgeo_best.pth)