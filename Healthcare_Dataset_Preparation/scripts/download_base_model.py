"""Downloads distilbert-base-uncased for train_security_classifier.py.

Plain `AutoTokenizer.from_pretrained("distilbert-base-uncased")` downloads fine but
can leave an empty snapshots/ dir on Windows setups without symlink privilege (Developer
Mode / admin) -- huggingface_hub falls back to symlinks by default and fails silently
there. `local_dir=` sidesteps the symlink cache entirely by writing real files.
"""
import os
from pathlib import Path

from huggingface_hub import snapshot_download

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # this repo's xet-transfer endpoint 404s

TARGET = Path(os.environ.get("BASE_MODEL_PATH", r"C:\dbu"))

if __name__ == "__main__":
    path = snapshot_download(
        "distilbert-base-uncased",
        local_dir=str(TARGET),
        allow_patterns=["*.json", "*.txt", "model.safetensors"],
    )
    print("downloaded to", path)
