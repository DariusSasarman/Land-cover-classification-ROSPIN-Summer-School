# Land Cover Classification Web Application

An end-to-end web architecture for satellite land-cover classification and explainability using fine-tuned deep learning models on Sentinel-2 imagery.

---

## 1. Overview & Supported Models

This repository provides training, evaluation, and deployment code for several baseline and deep learning models evaluated on the EuroSAT 10-class dataset:

| Model Architecture | Inputs / Bands | Accuracy | Macro F1 | Status / Role |
| :--- | :---: | :---: | :---: | :--- |
| **ResNet-18 (RGB)** | 3 Bands (RGB) | **97%**[cite: 2] | **0.97**[cite: 2] | **Production Web Model** (Active deployment) |
| **Spectral ResNet-18 (TorchGeo)** | 13 Bands (Multispectral) | **99%**[cite: 4] | **0.99**[cite: 4] | Evaluated / High-accuracy benchmark[cite: 4] |
| **ResNet-50 (RGB)** | 3 Bands (RGB) | **98%**[cite: 3] | **0.98**[cite: 3] | Evaluated / Large backbone benchmark[cite: 3] |
| **Spectral Random Forest** | Spectral Features | **87%**[cite: 5] | **0.86**[cite: 5] | Traditional ML baseline[cite: 5] |
| **Baseline Random Forest** | Basic Features | **80%**[cite: 1] | **0.78**[cite: 1] | Initial ML baseline[cite: 1] |

---

## 2. Model Selection Rationale for Web Deployment

While multiple architectures were trained, **ResNet-18 (RGB)** was selected as the live production model for the web application based on practical engineering constraints:

* **Production Choice — ResNet-18 (RGB)**: Reaches **97% accuracy**[cite: 2] with low memory usage and fast inference speed. It offers the ideal balance of accuracy and smooth frontend/backend integration.
* **Spectral ResNet-18 (13-Band Multispectral)**: Achieved the highest performance at **99% accuracy**[cite: 4], but was excluded from the live web pipeline due to time constraints and client-side integration complexity with multi-band GeoTIFF processing.
* **ResNet-50 (RGB)**: Reached **98% accuracy**[cite: 3], but was rejected for live hosting because its large size (~4+ GB) introduces significant storage overhead and memory latency during startup/inference.
* **Random Forest Baselines**: Ruled out due to insufficient accuracy (80%–87%)[cite: 1, 5] and their inability to learn spatial features critical for complex satellite imagery[cite: 1, 5].

---

## 3. Evaluation & Confusion Matrices

### **A. Production Model: ResNet-18 (RGB)**
* **Accuracy**: 97%[cite: 2] | **Macro F1**: 0.97[cite: 2]

                      precision    recall  f1-score   support

          AnnualCrop       0.90      0.97      0.93       450
              Forest       0.99      0.98      0.99       450
HerbaceousVegetation       0.96      0.98      0.97       450
             Highway       0.98      0.98      0.98       375
          Industrial       0.99      0.97      0.98       375
             Pasture       0.99      0.88      0.93       300
       PermanentCrop       0.95      0.94      0.94       375
         Residential       0.97      1.00      0.98       450
               River       0.97      0.97      0.97       375
             SeaLake       1.00      0.97      0.99       450

            accuracy                           0.97      4050
           macro avg       0.97      0.96      0.97      4050
        weighted avg       0.97      0.97      0.97      4050

Confusion Matrix:
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

---

### **B. Benchmark Model: Spectral ResNet-18 (TorchGeo 13-Band)**
* **Accuracy**: 99%[cite: 4] | **Macro F1**: 0.99[cite: 4]

                      precision    recall  f1-score   support

          AnnualCrop       0.99      0.99      0.99       450
              Forest       1.00      1.00      1.00       450
HerbaceousVegetation       0.99      0.99      0.99       450
             Highway       0.98      0.99      0.99       375
          Industrial       0.99      0.99      0.99       375
             Pasture       0.97      0.98      0.98       300
       PermanentCrop       0.99      0.99      0.99       375
         Residential       1.00      1.00      1.00       450
               River       0.99      0.99      0.99       375
             SeaLake       1.00      1.00      1.00       450

            accuracy                           0.99      4050
           macro avg       0.99      0.99      0.99      4050
        weighted avg       0.99      0.99      0.99      4050

Confusion Matrix:
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

---

### **C. Benchmark Model: ResNet-50 (RGB)**
* **Accuracy**: 98%[cite: 3] | **Macro F1**: 0.98[cite: 3]

                      precision    recall  f1-score   support

          AnnualCrop       0.97      0.97      0.97       450
              Forest       0.99      1.00      0.99       450
HerbaceousVegetation       0.99      0.96      0.97       450
             Highway       0.99      0.98      0.98       375
          Industrial       0.99      0.99      0.99       375
             Pasture       0.97      0.99      0.98       300
       PermanentCrop       0.97      0.96      0.97       375
         Residential       1.00      0.99      0.99       450
               River       0.98      0.99      0.99       375
             SeaLake       0.99      1.00      0.99       450

            accuracy                           0.98      4050
           macro avg       0.98      0.98      0.98      4050
        weighted avg       0.98      0.98      0.98      4050

Confusion Matrix:
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

---

### **D. Baseline: Spectral Random Forest**
* **Accuracy**: 87%[cite: 5] | **Macro F1**: 0.86[cite: 5]
* **Top Features**: `B12_mean` (0.0506), `B12_std` (0.0474), `R_B8_B12_std` (0.0465)[cite: 5].

                      precision    recall  f1-score   support

          AnnualCrop       0.90      0.90      0.90       450
              Forest       0.96      0.97      0.97       450
HerbaceousVegetation       0.89      0.91      0.90       450
             Highway       0.69      0.59      0.64       375
          Industrial       0.79      0.87      0.83       375
             Pasture       0.83      0.84      0.84       300
       PermanentCrop       0.81      0.80      0.80       375
         Residential       0.86      0.85      0.86       450
               River       0.90      0.95      0.92       375
             SeaLake       1.00      0.99      0.99       450

            accuracy                           0.87      4050
           macro avg       0.86      0.87      0.86      4050
        weighted avg       0.87      0.87      0.87      4050

Confusion Matrix:
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

---

### **E. Baseline: Standard Random Forest**
* **Accuracy**: 80%[cite: 1] | **Macro F1**: 0.78[cite: 1]

                      precision    recall  f1-score   support

          AnnualCrop       0.82      0.84      0.83       450
              Forest       0.92      0.96      0.94       450
HerbaceousVegetation       0.82      0.78      0.80       450
             Highway       0.52      0.40      0.45       375
          Industrial       0.88      0.90      0.89       375
             Pasture       0.80      0.87      0.84       300
       PermanentCrop       0.67      0.70      0.69       375
         Residential       0.77      0.89      0.83       450
               River       0.67      0.63      0.65       375
             SeaLake       0.97      0.90      0.94       450

            accuracy                           0.80      4050
           macro avg       0.78      0.79      0.78      4050
        weighted avg       0.79      0.80      0.79      4050

Confusion Matrix:
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

---

## 4. Known Issues & Real-World AOI Generalization

During testing on live Area of Interest (AOI) requests, the **Spectral ResNet-18** model exhibited domain shift errors—such as misclassifying industrial regions (e.g., ~64% industrial sites) as vegetation.

Key drivers of this discrepancy include:
1. **Spectral Channel & Normalization Mismatches**: Differences in band ordering and scaling between benchmark EuroSAT image patches and raw Sentinel-2 L2A tiles fetched dynamically via the Copernicus API.
2. **Spatial Mixed Pixels**: Real-world urban/industrial complexes contain mixed land covers (e.g., green roofs, surrounding grass patches) that contrast with EuroSAT's cropped single-label image tiles.