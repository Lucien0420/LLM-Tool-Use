"""CLI: CSV with a message column in → CSV with extracted columns out."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.services.csv_extract import extract_csv_to_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read CSV (UTF-8), extract fields from a text column, write CSV with extra columns",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Input CSV path",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output CSV path",
    )
    parser.add_argument(
        "--text-column",
        "-c",
        default="body",
        help="Column name containing the inquiry text (default: body)",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Append to generated column names if you need to avoid clashes (e.g. _extracted)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Process only the first N data rows (for quick demos)",
    )
    args = parser.parse_args()

    try:
        ok, err = extract_csv_to_csv(
            args.input,
            args.output,
            text_column=args.text_column,
            suffix=args.suffix,
            max_rows=args.limit,
        )
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(f"Done: {ok} ok, {err} failed/skipped. Output: {args.output.resolve()}")


if __name__ == "__main__":
    main()
