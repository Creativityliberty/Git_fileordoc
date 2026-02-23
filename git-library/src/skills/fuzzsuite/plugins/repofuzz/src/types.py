from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class RepoFuzzConfig:
    repo_path: str
    out_dir: str
    max_depth: int = 40
    max_files: int = 50_000
    max_file_bytes: int = 1_000_000
    ignore_dirs: List[str] = field(default_factory=lambda: [".git","node_modules","venv",".venv","__pycache__",".cache","dist","build"])

@dataclass
class FileNode:
    path: str
    layer: str
    sha1: str
    line_count: int
    import_count: int
    depends_on: List[str] = field(default_factory=list)
    risk: float = 0.0

@dataclass
class RepoIndex:
    repo_name: str
    files: Dict[str, FileNode]
    layers: Dict[str, List[str]]
    dependency_edges: List[Tuple[str,str]]
    layer_edges: List[Tuple[str,str,int]]
