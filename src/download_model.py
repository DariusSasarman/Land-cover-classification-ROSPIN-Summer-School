from asyncio import subprocess


def download_model(target_path):
  # Required packages
  import subprocess
  import sys
  import os
  import shutil
  from huggingface_hub import hf_hub_download

  # This is the repo where the model is stored
  REPO_ID = "dariussasarman/ROSPIN-Land-Classification"

  # These two download the files
  model_file = hf_hub_download(
      repo_id=REPO_ID,
      filename="model.py"
  )

  weights_file = hf_hub_download(
      repo_id=REPO_ID,
      filename="resnet18_m3_best.pth"
  )

  # Saving them to target location
  shutil.copy(model_file, os.path.join(target_path,"model.py"))
  shutil.copy(weights_file, os.path.join(target_path,"resnet18_m3_best.pth"))

  print("Model files downloaded successfully.")

# Should be able to be run as a stand-alone script 
if __name__ == "__main__":
  import os
  # Usually would be run in "repo/src" => small "cd .."
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  # Download model to "repo/model"
  model_path = os.path.join(repo_root, "model")
  os.makedirs(model_path,exist_ok=True)
  # Create an empty __init__.py file in the model directory to make it a package
  open(os.path.join(model_path, "__init__.py"), "a").close()
  download_model(model_path)
