from __future__ import annotations
from typing import Dict, List

SEV = {"forbidden_layer_edge":"high","god_file":"medium","hotspot":"medium"}

def build_refactor_plan(vr: dict, templates: dict) -> dict:
    tmpl = (templates or {}).get("templates", {})
    items = []
    for v in (vr.get("violations") or []):
        kind = v.get("kind")
        items.append({
            "kind": kind,
            "path": v.get("path"),
            "severity": SEV.get(kind, "low"),
            "recommendations": list(tmpl.get(kind, [])),
            "context": v.get("details") or {},
        })
    items.sort(key=lambda x: {"high":0,"medium":1,"low":2}.get(x["severity"], 3))
    return {"repo": vr.get("repo","unknown"), "items": items}
