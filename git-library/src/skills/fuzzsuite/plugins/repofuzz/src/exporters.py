from __future__ import annotations
import os, yaml
from collections import Counter

def export_repo_index_yaml(idx, path: str) -> None:
    obj = {
        "repo_name": idx.repo_name,
        "layers": idx.layers,
        "dependency_edges": idx.dependency_edges,
        "layer_edges": idx.layer_edges,
        "files": {
            p: {
                "layer": n.layer,
                "sha1": n.sha1,
                "line_count": n.line_count,
                "import_count": n.import_count,
                "risk": n.risk,
                "depends_on": n.depends_on,
            } for p, n in idx.files.items()
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False)

def export_architecture_md(idx, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("# ARCHITECTURE\n\n")
        f.write(f"- repo: `{idx.repo_name}`\n")
        f.write(f"- files: `{len(idx.files)}`\n\n")
        f.write("## Layers\n\n")
        for layer, paths in sorted(idx.layers.items()):
            f.write(f"### {layer} ({len(paths)})\n")
            for p in paths[:120]:
                n = idx.files[p]
                f.write(f"- `{p}` — {n.line_count} lines, {n.import_count} imports, risk {n.risk:.2f}\n")
            if len(paths) > 120:
                f.write(f"- … +{len(paths)-120} more\n")
            f.write("\n")

def export_layers_mermaid(idx, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("graph LR\n")
        for l in sorted(idx.layers.keys()):
            f.write(f'  {l}["{l}"]\n')
        for a,b,c in idx.layer_edges[:80]:
            f.write(f"  {a} -->|{c}| {b}\n")

def export_deps_top_mermaid(idx, path: str, max_nodes: int = 40, max_edges: int = 80) -> None:
    out_deg = Counter()
    in_deg = Counter()
    for a,b in idx.dependency_edges:
        out_deg[a] += 1
        in_deg[b] += 1
    top = set([p for p,_ in out_deg.most_common(max_nodes//2)] + [p for p,_ in in_deg.most_common(max_nodes//2)])
    edges = [(a,b) for a,b in idx.dependency_edges if a in top and b in top][:max_edges]

    def sid(p: str) -> str:
        import hashlib
        return "n"+hashlib.md5(p.encode("utf-8")).hexdigest()[:10]

    with open(path, "w", encoding="utf-8") as f:
        f.write("graph LR\n")
        for p in sorted(top):
            f.write(f'{sid(p)}["{p}"]\n')
        for a,b in edges:
            f.write(f"  {sid(a)} --> {sid(b)}\n")

def export_violations_yaml_md(vr: dict, out_dir: str, max_items: int = 200) -> None:
    ypath = os.path.join(out_dir, "violations.yaml")
    with open(ypath, "w", encoding="utf-8") as f:
        yaml.safe_dump(vr, f, allow_unicode=True, sort_keys=False)

    by = {}
    for v in (vr.get("violations") or []):
        by.setdefault(v.get("kind","unknown"), []).append(v)

    mpath = os.path.join(out_dir, "VIOLATIONS.md")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write("# VIOLATIONS (STRICT MODE)\n\n")
        f.write(f"- repo: `{vr.get('repo','unknown')}`\n")
        f.write(f"- total: `{len(vr.get('violations') or [])}`\n\n")
        for kind, items in sorted(by.items()):
            f.write(f"## {kind} ({len(items)})\n\n")
            for v in items[:max_items]:
                det = v.get("details") or {}
                ds = ", ".join([f"{k}={val}" for k,val in det.items()])
                f.write(f"- `{v.get('path')}`" + (f" — {ds}" if ds else "") + "\n")
            if len(items) > max_items:
                f.write(f"- … +{len(items)-max_items} more\n")
            f.write("\n")

def export_refactor_yaml_md(plan: dict, out_dir: str, max_items: int = 300) -> None:
    ypath = os.path.join(out_dir, "refactor_plan.yaml")
    with open(ypath, "w", encoding="utf-8") as f:
        yaml.safe_dump(plan, f, allow_unicode=True, sort_keys=False)

    mpath = os.path.join(out_dir, "REFACTOR_PLAN.md")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write("# REFACTOR PLAN\n\n")
        f.write(f"- repo: `{plan.get('repo','unknown')}`\n")
        f.write(f"- items: `{len(plan.get('items') or [])}`\n\n")
        for it in (plan.get("items") or [])[:max_items]:
            f.write(f"## {it.get('severity','').upper()} — {it.get('kind')}\n\n")
            f.write(f"- path: `{it.get('path')}`\n")
            ctx = it.get("context") or {}
            if ctx:
                f.write("- context:\n")
                for k,v in ctx.items():
                    f.write(f"  - {k}: {v}\n")
            recs = it.get("recommendations") or []
            if recs:
                f.write("\n### Recommendations\n")
                for r in recs:
                    f.write(f"- {r}\n")
            f.write("\n")
        if len(plan.get("items") or []) > max_items:
            f.write(f"… +{len(plan.get('items') or [])-max_items} more\n")
