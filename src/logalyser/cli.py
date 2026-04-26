"""
cli.py - Command-line interface for logalyser.
"""

import argparse
import sys
from pathlib import Path

from .parser import parse_log
from .analyser import analyse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logalyser",
        description="Analyse warehouse automation system log files for patterns and anomalies.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- analyse subcommand ---
    analyse_cmd = subparsers.add_parser(
        "analyse",
        help="Analyse a log file and print a summary report.",
    )
    analyse_cmd.add_argument(
        "logfile",
        type=Path,
        help="Path to a log file (.log or .log.bz2).",
    )
    analyse_cmd.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Number of top messages to display (default: 10).",
    )
    analyse_cmd.add_argument(
        "--level",
        choices=["INFO", "WARNING", "ERROR", "FATAL"],
        default=None,
        help="Filter output to a specific severity level.",
    )

    return parser


def cmd_analyse(args: argparse.Namespace) -> int:
    try:
        entries = list(parse_log(args.logfile))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.level:
        entries = [e for e in entries if e.level == args.level]

    if not entries:
        print("No matching log entries found.")
        return 0

    result = analyse(entries, top_n=args.top)
    _print_report(result, args)
    return 0


def _print_report(result, args) -> None:
    width = 64

    def rule():
        print("-" * width)

    def section(title):
        print(f"\n{'=' * width}")
        print(f"  {title}")
        print(f"{'=' * width}")

    section("LOGALYSER REPORT")

    print(f"  File analysed : {args.logfile}")
    if result.time_start and result.time_end:
        print(f"  Time range    : {result.time_start:%d/%m/%Y %H:%M:%S}"
              f"  →  {result.time_end:%d/%m/%Y %H:%M:%S}")
    print(f"  Total entries : {result.total_entries}")

    section("ENTRIES BY SEVERITY")
    for level in ("FATAL", "ERROR", "WARNING", "INFO"):
        count = result.level_counts.get(level, 0)
        bar = "█" * min(count, 40)
        print(f"  {level:<8}  {count:>5}  {bar}")

    section("ENTRIES BY PROCESS")
    for process, count in result.process_counts.most_common():
        bar = "█" * min(count, 40)
        print(f"  {process:<12}  {count:>5}  {bar}")

    section("ERRORS & WARNINGS BY PROCESS")
    for process, entries in sorted(result.errors_by_process.items()):
        print(f"\n  [{process}]  ({len(entries)} events)")
        rule()
        for entry in entries:
            print(f"  {entry.timestamp:%H:%M:%S}  {entry.level:<8}  {entry.message}")

    section("ACTIVITY TIMELINE  (entries per hour)")
    for hour, count in sorted(result.entries_by_hour.items()):
        bar = "█" * min(count, 40)
        print(f"  {hour}   {count:>4}  {bar}")

    section(f"TOP {len(result.top_messages)} MOST FREQUENT MESSAGES")
    for msg, count in result.top_messages.most_common():
        print(f"  {count:>4}x  {msg}")

    print(f"\n{'=' * width}\n")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyse":
        sys.exit(cmd_analyse(args))


if __name__ == "__main__":
    main()