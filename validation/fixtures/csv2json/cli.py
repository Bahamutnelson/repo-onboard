"""csv2json — a command-line tool that converts a CSV file to JSON.

Exposed as the `csv2json` console script (see setup.py).
"""
import argparse
import csv
import json
import sys


def convert(infile, outfile, *, delimiter=",", indent=2):
    """Read CSV rows from `infile` and write a JSON array to `outfile`."""
    reader = csv.DictReader(infile, delimiter=delimiter)
    rows = list(reader)
    json.dump(rows, outfile, indent=indent)
    outfile.write("\n")
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="csv2json",
        description="Convert a CSV file to JSON.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="input CSV file (default: stdin)",
    )
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="output JSON file (default: stdout)",
    )
    parser.add_argument(
        "-d", "--delimiter",
        default=",",
        help="CSV field delimiter (default: ',')",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation (default: 2)",
    )
    args = parser.parse_args(argv)

    n = convert(args.input, args.output, delimiter=args.delimiter, indent=args.indent)
    print(f"converted {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
