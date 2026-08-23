# Land-cover-classification-ROSPIN-Summer-School

Project developed during [Rospin Summer School](https://github.com/Romanian-Space-Initiative).

This project targets the task of *Land use land cover classification task* using machine learning.

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

<sub> Currently, said map isn't saved.</sub>

### 6. Etc ( work in progress )