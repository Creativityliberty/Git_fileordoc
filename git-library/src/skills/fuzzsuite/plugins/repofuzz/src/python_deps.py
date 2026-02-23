from __future__ import annotations
import os, re
from typing import Dict, Optional, Set, List, Tuple

_IMPORT_RE = re.compile(r"^(import\s+|from\s+)([A-Za-z0-9_\.]+)")

def build_module_map(py_files: List[str]) -> Dict[str,str]:
    m = {}
    for rp in py_files:
        rp = rp.replace("\\","/")
        if rp.endswith("__init__.py"):
            pkg = rp[:-len("/__init__.py")] if rp.endswith("/__init__.py") else ""
            if pkg:
                m[pkg.replace("/", ".")] = rp
        else:
            m[rp[:-3].replace("/", ".")] = rp
    return m

def _resolve(module_map: Dict[str,str], mod: str) -> Optional[str]:
    parts = mod.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in module_map:
            return module_map[cand]
    return None

def extract_modules(abs_path: str) -> Set[str]:
    mods = set()
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not (s.startswith("import ") or s.startswith("from ")):
                    continue
                m = _IMPORT_RE.match(s)
                if m:
                    mods.add(m.group(2))
    except Exception:
        pass
    return mods

def analyze(repo_abs: str, rel_py_files: List[str]) -> Tuple[Dict[str,List[str]], List[Tuple[str,str]], Dict[str,int]]:
    module_map = build_module_map(rel_py_files)
    deps = {}
    edges = set()
    import_counts = {}
    for rp in rel_py_files:
        abs_path = os.path.join(repo_abs, rp)
        mods = extract_modules(abs_path)
        import_counts[rp] = 0
        for mod in mods:
            t = _resolve(module_map, mod)
            if t and t != rp:
                deps.setdefault(rp, []).append(t)
                edges.add((rp, t))
            import_counts[rp] += 1
    return deps, sorted(list(edges)), import_counts
