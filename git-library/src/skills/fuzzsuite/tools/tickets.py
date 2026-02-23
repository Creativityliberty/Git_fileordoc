from __future__ import annotations
import os, csv, yaml
from typing import Any, Dict, List
from fuzzsuite.core.io import ensure_dir

def _load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def tickets_main(plan_path: str, out_dir: str) -> None:
    ensure_dir(out_dir)
    plan = _load_yaml(plan_path) or {}
    repo = plan.get("repo", "unknown")
    items = plan.get("items", []) or []

    # GitHub issues markdown (one section per item)
    gh_path = os.path.join(out_dir, "GITHUB_ISSUES.md")
    with open(gh_path, "w", encoding="utf-8") as f:
        f.write(f"# GitHub Issues — {repo}\n\n")
        for i, it in enumerate(items, 1):
            title = f"[{it.get('severity','').upper()}] {it.get('kind')} — {it.get('path')}"
            f.write(f"## {i}. {title}\n\n")
            ctx = it.get("context") or {}
            if ctx:
                f.write("**Context**\n\n")
                for k, v in ctx.items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
            recs = it.get("recommendations") or []
            if recs:
                f.write("**Recommendations**\n\n")
                for r in recs:
                    f.write(f"- {r}\n")
                f.write("\n")
            f.write("---\n\n")

    # Jira CSV (import-friendly)
    jira_path = os.path.join(out_dir, "JIRA_IMPORT.csv")
    with open(jira_path, "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(["Summary", "Description", "Issue Type", "Priority"])
        for it in items:
            summary = f"{it.get('kind')} — {it.get('path')}"
            desc_lines = []
            ctx = it.get("context") or {}
            for k, v in ctx.items():
                desc_lines.append(f"{k}: {v}")
            recs = it.get("recommendations") or []
            if recs:
                desc_lines.append("Recommendations:")
                desc_lines.extend([f"- {r}" for r in recs])
            description = "\n".join(desc_lines)
            issue_type = "Task"
            sev = (it.get("severity") or "low").lower()
            priority = {"high":"Highest","medium":"High","low":"Medium"}.get(sev, "Medium")
            w.writerow([summary, description, issue_type, priority])
