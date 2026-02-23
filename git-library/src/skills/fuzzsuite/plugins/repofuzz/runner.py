from __future__ import annotations
import os
from fuzzsuite.core.io import ensure_dir
from fuzzsuite.plugins.repofuzz.src.indexer import build_index, RepoFuzzConfig
from fuzzsuite.plugins.repofuzz.src.rules import load_rules
from fuzzsuite.plugins.repofuzz.src.violations import compute_violations
from fuzzsuite.plugins.repofuzz.src.templates import load_templates
from fuzzsuite.plugins.repofuzz.src.refactor import build_refactor_plan
from fuzzsuite.plugins.repofuzz.src.exporters import (
    export_repo_index_yaml,
    export_architecture_md,
    export_layers_mermaid,
    export_deps_top_mermaid,
    export_violations_yaml_md,
    export_refactor_yaml_md,
)

def run_repofuzz_analyze(repo: str, out_dir: str, strict: bool, rules: str|None, templates: str|None) -> int:
    cfg = RepoFuzzConfig(repo_path=repo, out_dir=out_dir)
    idx = build_index(cfg)
    ensure_dir(out_dir)

    export_repo_index_yaml(idx, os.path.join(out_dir, "repo_index.yaml"))
    export_architecture_md(idx, os.path.join(out_dir, "ARCHITECTURE.md"))
    export_layers_mermaid(idx, os.path.join(out_dir, "layers.mmd"))
    export_deps_top_mermaid(idx, os.path.join(out_dir, "deps_top.mmd"), max_nodes=40, max_edges=80)

    vr = None
    if rules or strict:
        r = load_rules(rules)
        vr = compute_violations(idx, r)
        export_violations_yaml_md(vr, out_dir, max_items=r["max_items_per_section"])

    if templates:
        t = load_templates(templates)
        if vr is None:
            r = load_rules(rules)
            vr = compute_violations(idx, r)
        plan = build_refactor_plan(vr, t)
        export_refactor_yaml_md(plan, out_dir, max_items=300)

    if strict and vr is not None and len(vr["violations"]) > 0:
        return 2
    return 0
