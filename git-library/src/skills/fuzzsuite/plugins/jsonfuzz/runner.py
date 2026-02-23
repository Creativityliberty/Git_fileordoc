from __future__ import annotations
import os, json
from fuzzsuite.core.io import ensure_dir

EXTS = {".json",".md",".toml",".yaml",".yml"}

def run_jsonfuzz_index(input_dir: str, out_dir: str, max_bytes: int = 1_000_000) -> None:
    ensure_dir(out_dir)
    manifest = {"input": os.path.abspath(input_dir), "files": []}
    for root, _, files in os.walk(input_dir):
        for fn in files:
            _, ext = os.path.splitext(fn.lower())
            if ext not in EXTS:
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, input_dir).replace("\\","/")
            try:
                size = os.path.getsize(p)
            except Exception:
                size = None
            entry = {"path": rel, "bytes": size}
            if size is not None and size <= max_bytes:
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        head = f.read(400)
                    entry["preview"] = " ".join(head.split())
                except Exception:
                    pass
            manifest["files"].append(entry)

    with open(os.path.join(out_dir, "jsonfuzz_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
