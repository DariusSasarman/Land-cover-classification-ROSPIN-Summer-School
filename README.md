# Land-cover-classification-ROSPIN-Summer-School

Project developed during [Rospin Summer School](https://github.com/Romanian-Space-Initiative).

This project targets the task of *Land use land cover classification task* using machine learning.

### Fine-tune the local 13-band `.pth` model

The checkpoint `notebooks/resnet18_sentinel2_all_moco.pth` contains the
pretrained 13-band ResNet-18 backbone. Fine-tune it on labeled multispectral
GeoTIFFs with:

```bash
python ./src/train_spectral_resnet_torchgeo.py `
  --weights ./notebooks/resnet18_sentinel2_all_moco.pth
```

The current loader expects one directory per EuroSAT class under
`data/raw/EuroSATallBands`, with 13 bands in Sentinel-2 order and reflectance
values scaled by 10000. It creates a new 10-class head and saves the best
fine-tuned model to `checkpoints/spectral_resnet_torchgeo_best.pth`.

For a different dataset, keep the same labeled-folder structure and update
`CLASS_NAMES`, `BAND_ORDER`, and `SPLITS_PATH` in
`src/train_spectral_resnet_torchgeo.py` to match its labels and split file.

## Developer Setup Steps

### 0. Switch to virtual environment and install requirements.txt

```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```

### 1. Download the model itself

```bash

python3 ./src/download_model.py

```

Also available [here](https://huggingface.co/dariussasarman/ROSPIN-Land-Classification).

Hosted on Hugging Face because weights are too big for a git repo.

You should see a "./model" folder appear.

This step downloads / instantiates the fine-tuned model.

### 2. Download the Sentinel-2 data

```bash

python3 ./src/download_sentinel2_copernicus.py

```

or 

```bash

python3 ./src/download_sentinel2.py

```

Both scripts should download similar "./data/raw/sentinel2_aoi.tif".

The first one uses the Copernicus api and the second one uses the Google Earth Engine.

### 3. Tile the Sentinel-2 image

```bash

python3 ./src/tile_and_prepare_inference.py

```

Should see "./data/processed/tiles" appear.

This step tiles the Sentinel-2 data of our target location.

### 4. Run inference on the target tiles

#### !!! This step is computationally intensive. Run it on a machine capable of handling it !!!

```bash

python3 ./src/run_inference.py

```

Should see "./data/processed/tiles/predictions.npy" appear.

This step runs inference on the specified location.

### 5. Display inference on the map

```bash

python3 ./src/export_inference_map.py

```

A window should appear on your screen.

The map inside said window represents the inference applied on the map.

You can zoom in/out and change the the transparency level of the classification.

There's also a button that saves the current state of the plot as a png.
