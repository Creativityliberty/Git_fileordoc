from __future__ import annotations
import argparse
from fuzzsuite.core.plugin import FuzzPlugin
from fuzzsuite.plugins.repofuzz.runner import run_repofuzz_analyze

class RepoFuzzPlugin(FuzzPlugin):
    name = "repofuzz"

    def register(self, subparsers: argparse._SubParsersAction) -> None:
        p = subparsers.add_parser("repofuzz", help="RepoFuzz plugin")
        sp = p.add_subparsers(dest="subcmd", required=True)

        pa = sp.add_parser("analyze", help="Analyze a repo (deps/layers) + strict + refactor + mermaid")
        pa.add_argument("--repo", required=True)
        pa.add_argument("--out", required=True)
        pa.add_argument("--strict", action="store_true")
        pa.add_argument("--rules", default=None)
        pa.add_argument("--templates", default=None)

        def _handler(args):
            code = run_repofuzz_analyze(
                repo=args.repo,
                out_dir=args.out,
                strict=args.strict,
                rules=args.rules,
                templates=args.templates,
            )
            raise SystemExit(code)

        pa.set_defaults(_handler=_handler)
