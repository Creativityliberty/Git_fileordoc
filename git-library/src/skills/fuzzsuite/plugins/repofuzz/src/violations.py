from __future__ import annotations
from typing import Dict, List, Tuple
from .types import RepoIndex

def compute_violations(idx: RepoIndex, rules: dict) -> dict:
    forbid = set(rules.get("forbidden_layer_edges", []))
    god_lines = int(rules.get("god_file_lines", 800))
    hotspot = float(rules.get("hotspot_risk", 3.0))
    violations = []

    # thresholds
    for p, n in idx.files.items():
        if n.line_count >= god_lines:
            violations.append({"kind":"god_file","path":p,"details":{"lines":str(n.line_count),"threshold":str(god_lines)}})
        if n.risk >= hotspot:
            violations.append({"kind":"hotspot","path":p,"details":{"risk":f"{n.risk:.2f}","threshold":str(hotspot)}})

    # forbidden layer edges
    for a,b in idx.dependency_edges:
        la = idx.files[a].layer
        lb = idx.files[b].layer
        if (la, lb) in forbid:
            violations.append({"kind":"forbidden_layer_edge","path":a,"details":{"from_layer":la,"to_layer":lb,"to":b}})

    return {"repo": idx.repo_name, "violations": violations}
