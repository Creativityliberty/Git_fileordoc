from __future__ import annotations
import argparse
from dotenv import load_dotenv

from fuzzsuite.plugins.repofuzz.plugin import RepoFuzzPlugin
from fuzzsuite.plugins.jsonfuzz.plugin import JSONFuzzPlugin
from fuzzsuite.tools.tickets import tickets_main
from fuzzsuite.tools.check import check_main

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(prog="fuzzsuite", description="FuzzSuite v3")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # plugins
    RepoFuzzPlugin().register(sub)
    JSONFuzzPlugin().register(sub)

    # tools
    pt = sub.add_parser("tickets", help="Generate GitHub/Jira tickets from refactor_plan.yaml")
    pt.add_argument("--plan", required=True)
    pt.add_argument("--out", required=True)

    pc = sub.add_parser("check", help="CI check: exit non-zero if strict violations exist")
    pc.add_argument("--repo", required=True)
    pc.add_argument("--rules", required=True)
    pc.add_argument("--out", default=".fuzzsuite_check_out")

    args = parser.parse_args()

    if args.cmd == "tickets":
        tickets_main(args.plan, args.out)
        return

    if args.cmd == "check":
        raise SystemExit(check_main(repo=args.repo, rules=args.rules, out_dir=args.out))

    # plugin commands: parser attaches _handler on plugin root parser
    if hasattr(args, "_handler"):
        args._handler(args)
