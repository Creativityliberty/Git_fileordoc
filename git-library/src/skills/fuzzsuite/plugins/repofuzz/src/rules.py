from __future__ import annotations
import yaml

def load_rules(path: str | None) -> dict:
    # returns dict with forbidden edges + thresholds
    out = {
        "forbidden_layer_edges": [],
        "god_file_lines": 800,
        "hotspot_risk": 3.0,
        "max_items_per_section": 200,
    }
    if not path:
        return out
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    forbid = (((data.get("layers") or {}).get("forbid")) or [])
    out["forbidden_layer_edges"] = [(str(x.get("from")), str(x.get("to"))) for x in forbid if x and x.get("from") and x.get("to")]
    limits = data.get("limits") or {}
    out["god_file_lines"] = int(limits.get("god_file_lines", out["god_file_lines"]))
    out["hotspot_risk"] = float(limits.get("hotspot_risk", out["hotspot_risk"]))
    report = data.get("report") or {}
    out["max_items_per_section"] = int(report.get("max_items_per_section", out["max_items_per_section"]))
    return out
