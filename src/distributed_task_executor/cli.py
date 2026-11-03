import argparse
import sys

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


def main() -> int:
    args = build_parser().parse_args()
    print(f"{args.subcommand}: not implemented yet", file=sys.stderr)
    return 1
