import os
from huggingface_hub import hf_hub_download
from app.logger import get_logger

logger = get_logger("ml_engine.ModelDownloader")

REPO_ID = "Airam18/land-cover-clasification-model-all-bands"
WEIGHTS_FILENAME = "spectral_resnet_torchgeo_best.pth"


def download_model_weights(target_path: str) -> None:
    weights_path = os.path.join(target_path, WEIGHTS_FILENAME)

    if os.path.exists(weights_path):
        logger.debug("Model weights already present at %s", weights_path)
        return

    logger.info("Downloading model weights from HuggingFace repo '%s' to %s...", REPO_ID, weights_path)
    weights_file = hf_hub_download(
        repo_id=REPO_ID,
        filename=WEIGHTS_FILENAME,
        repo_type="model",
    )

    os.makedirs(target_path, exist_ok=True)
    with open(weights_file, "rb") as source, open(weights_path, "wb") as target:
        target.write(source.read())

    logger.info("Model weights downloaded and saved successfully to %s", weights_path)


if __name__ == "__main__":
    target = os.path.dirname(os.path.abspath(__file__))
    download_model_weights(target)