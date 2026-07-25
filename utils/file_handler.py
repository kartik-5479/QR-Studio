from pathlib import Path


def ensure_directory(path):
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
