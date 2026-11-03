import argparse
import sys
from collections.abc import Sequence

SUBCOMMANDS = {
    "demo": "Run the recovery demo",
    "api": "Run the API Listener",
    "worker": "Run a Worker",
    "watchdog": "Run the Orchestrator Watchdog",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="distributed-task-executor")
    subcommands = parser.add_subparsers(dest="subcommand", required=True)
    for name, description in SUBCOMMANDS.items():
        subcommands.add_parser(name, help=description)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"{args.subcommand}: not implemented yet", file=sys.stderr)
    return 1
