from __future__ import annotations
import os
from collections import Counter
from typing import Dict, List, Tuple
from .types import RepoFuzzConfig, RepoIndex, FileNode
from .layer import detect_layer
from .hashing import sha1_bytes
from .python_deps import analyze as analyze_py

def _iter_files(repo_abs: str, cfg: RepoFuzzConfig) -> List[str]:
    out = []
    for root, dirs, files in os.walk(repo_abs):
        # prune dirs
        dirs[:] = [d for d in dirs if d not in cfg.ignore_dirs and not d.startswith(".")]
        for fn in files:
            if fn.startswith("."):
                continue
            abs_p = os.path.join(root, fn)
            rel = os.path.relpath(abs_p, repo_abs).replace("\\","/")
            out.append(rel)
            if len(out) >= cfg.max_files:
                return out
    return out

def build_index(cfg: RepoFuzzConfig) -> RepoIndex:
    repo_abs = os.path.abspath(cfg.repo_path)
    repo_name = os.path.basename(repo_abs)
    rel_files = _iter_files(repo_abs, cfg)

    py_files = [p for p in rel_files if p.endswith(".py")]
    deps_map, edges, import_counts = analyze_py(repo_abs, py_files)

    files: Dict[str, FileNode] = {}
    layers: Dict[str, List[str]] = {}

    for rel in rel_files:
        abs_p = os.path.join(repo_abs, rel)
        try:
            b = open(abs_p, "rb").read(cfg.max_file_bytes)
        except Exception:
            b = b""
        sha1 = sha1_bytes(b)
        try:
            with open(abs_p, "r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)
        except Exception:
            line_count = 0
        layer = detect_layer(rel)
        ic = import_counts.get(rel, 0)
        dep_list = deps_map.get(rel, [])
        risk = (line_count / 500.0) + (ic * 0.3)
        files[rel] = FileNode(path=rel, layer=layer, sha1=sha1, line_count=line_count, import_count=ic, depends_on=dep_list, risk=risk)
        layers.setdefault(layer, []).append(rel)

    # layer edges counts
    cnt = Counter()
    for a,b in edges:
        cnt[(files[a].layer, files[b].layer)] += 1
    layer_edges = [(a,b,c) for (a,b),c in cnt.most_common()]

    # sort layers lists
    for k in layers:
        layers[k] = sorted(layers[k])

    return RepoIndex(repo_name=repo_name, files=files, layers=layers, dependency_edges=edges, layer_edges=layer_edges)
