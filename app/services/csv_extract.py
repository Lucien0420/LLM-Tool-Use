"""CSV row-wise extraction: one column holds inquiry text → append structured columns."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from app.services.extract import InquiryExtractService

logger = logging.getLogger(__name__)

EXTRACT_KEYS = ("customer_name", "contact", "estimated_budget", "error")


def _output_column_names(
    input_fieldnames: list[str],
    *,
    suffix: str,
) -> dict[str, str]:
    """Map logical keys to CSV column names; avoid collisions with input headers."""
    existing = set(input_fieldnames)
    out: dict[str, str] = {}
    for key in EXTRACT_KEYS:
        base = key + suffix
        name = base
        n = 0
        while name in existing:
            n += 1
            name = f"{base}_{n}"
        existing.add(name)
        out[key] = name
    return out


def extract_csv_to_csv(
    input_csv: Path,
    output_csv: Path,
    *,
    text_column: str,
    service: InquiryExtractService | None = None,
    suffix: str = "",
    max_rows: int | None = None,
) -> tuple[int, int]:
    """
    Read UTF-8 (with BOM) CSV; for each row, read inquiry text from ``text_column``;
    append extraction columns. Returns (success_count, error_count) where error means
    empty text or exception during extraction (row still written).

    If ``max_rows`` is set, only the first N **data** rows are read (after the header).
    """
    input_csv = input_csv.resolve()
    if not input_csv.is_file():
        raise FileNotFoundError(f"Not a file: {input_csv}")

    svc = service or InquiryExtractService()

    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        fieldnames = list(reader.fieldnames)
        if text_column not in fieldnames:
            raise ValueError(
                f"Column {text_column!r} not in CSV. Found: {fieldnames}",
            )

        out_cols = _output_column_names(fieldnames, suffix=suffix)
        output_fieldnames = fieldnames + [out_cols[k] for k in EXTRACT_KEYS]

        output_csv.parent.mkdir(parents=True, exist_ok=True)
        ok, err = 0, 0

        with output_csv.open("w", encoding="utf-8-sig", newline="") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=output_fieldnames)
            writer.writeheader()

            n_seen = 0
            for row in reader:
                if max_rows is not None and n_seen >= max_rows:
                    break
                n_seen += 1
                out_row: dict[str, str] = {k: (row.get(k) or "") for k in fieldnames}
                text = (row.get(text_column) or "").strip()

                if not text:
                    out_row[out_cols["customer_name"]] = ""
                    out_row[out_cols["contact"]] = ""
                    out_row[out_cols["estimated_budget"]] = ""
                    out_row[out_cols["error"]] = "empty message column"
                    err += 1
                    writer.writerow(out_row)
                    continue

                try:
                    r = svc.extract_from_text(text)
                    out_row[out_cols["customer_name"]] = r.customer_name or ""
                    out_row[out_cols["contact"]] = r.contact or ""
                    out_row[out_cols["estimated_budget"]] = r.estimated_budget or ""
                    out_row[out_cols["error"]] = ""
                    ok += 1
                except Exception as e:
                    logger.exception("csv row extract failed")
                    out_row[out_cols["customer_name"]] = ""
                    out_row[out_cols["contact"]] = ""
                    out_row[out_cols["estimated_budget"]] = ""
                    out_row[out_cols["error"]] = str(e)
                    err += 1

                writer.writerow(out_row)

    return ok, err
