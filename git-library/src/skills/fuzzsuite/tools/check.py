from __future__ import annotations
import os, subprocess, sys
from fuzzsuite.plugins.repofuzz.runner import run_repofuzz_analyze

def check_main(repo: str, rules: str, out_dir: str) -> int:
    # reuse repofuzz plugin runner in strict mode; return exit code 0/2
    return run_repofuzz_analyze(repo=repo, out_dir=out_dir, strict=True, rules=rules, templates=None)
