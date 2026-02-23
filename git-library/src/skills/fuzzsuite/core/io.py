from __future__ import annotations
import os, yaml

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def dump_yaml(obj, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False)

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
