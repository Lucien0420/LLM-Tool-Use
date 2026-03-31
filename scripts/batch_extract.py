"""CLI: batch folder of .txt files (one inquiry per file) → one CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.services.batch import extract_folder_to_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract many inquiries from a folder into one CSV",
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        type=Path,
        required=True,
        help="Folder containing one .txt file per inquiry",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output CSV path (e.g. out.csv)",
    )
    parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern for files (default: *.txt)",
    )
    args = parser.parse_args()

    try:
        ok, err = extract_folder_to_csv(
            args.input_dir,
            args.output,
            pattern=args.pattern,
        )
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(f"Done: {ok} ok, {err} failed. Output: {args.output.resolve()}")


if __name__ == "__main__":
    main()
