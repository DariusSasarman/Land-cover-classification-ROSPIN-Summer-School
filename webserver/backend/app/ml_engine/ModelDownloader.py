import os
import shutil

from huggingface_hub import hf_hub_download

REPO_ID = "dariussasarman/ROSPIN-Land-Classification"


def download_model_weights(target_path: str) -> None:
    weights_path = os.path.join(target_path, "resnet18_m3_best.pth")

    if os.path.exists(weights_path):
        return

    weights_file = hf_hub_download(repo_id=REPO_ID, filename="resnet18_m3_best.pth")

    os.makedirs(target_path, exist_ok=True)
    shutil.copy(weights_file, weights_path)

    print("Model weights downloaded successfully.")


if __name__ == "__main__":
    target = os.path.dirname(os.path.abspath(__file__))
    download_model_weights(target)