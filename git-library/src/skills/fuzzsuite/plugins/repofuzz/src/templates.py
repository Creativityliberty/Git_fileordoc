from __future__ import annotations
import yaml

def load_templates(path: str | None) -> dict:
    if not path:
        return {"templates": {}}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "templates" not in data:
        data["templates"] = {}
    return data
