from __future__ import annotations
import argparse
from fuzzsuite.core.plugin import FuzzPlugin
from fuzzsuite.plugins.jsonfuzz.runner import run_jsonfuzz_index

class JSONFuzzPlugin(FuzzPlugin):
    name = "jsonfuzz"

    def register(self, subparsers: argparse._SubParsersAction) -> None:
        p = subparsers.add_parser("jsonfuzz", help="JSONFuzz plugin")
        sp = p.add_subparsers(dest="subcmd", required=True)

        pi = sp.add_parser("index", help="Index a folder of json/md/toml/yaml and export a manifest")
        pi.add_argument("--input", required=True)
        pi.add_argument("--out", required=True)
        pi.add_argument("--max-bytes", type=int, default=1_000_000)

        def _handler(args):
            run_jsonfuzz_index(args.input, args.out, args.max_bytes)

        pi.set_defaults(_handler=_handler)
