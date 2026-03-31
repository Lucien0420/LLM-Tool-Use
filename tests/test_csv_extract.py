from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.csv_extract import extract_csv_to_csv


def test_extract_csv_to_csv_mocked(tmp_path: Path):
    inp = tmp_path / "in.csv"
    inp.write_text(
        "id,body\n"
        '1,"hello name A phone 1 budget 10"\n'
        '2,"name B email@x.com budget 20"\n',
        encoding="utf-8",
    )
    out = tmp_path / "out.csv"

    mock_svc = MagicMock()
    mock_svc.extract_from_text.side_effect = [
        SimpleNamespace(customer_name="A", contact="1", estimated_budget="10"),
        SimpleNamespace(customer_name="B", contact="email@x.com", estimated_budget="20"),
    ]

    ok, err = extract_csv_to_csv(inp, out, text_column="body", service=mock_svc)
    assert ok == 2 and err == 0
    text = out.read_text(encoding="utf-8-sig")
    assert "A" in text and "B" in text


def test_extract_csv_missing_column(tmp_path: Path):
    inp = tmp_path / "in.csv"
    inp.write_text("id,x\n1,y\n", encoding="utf-8")
    with pytest.raises(ValueError, match="body"):
        extract_csv_to_csv(inp, tmp_path / "o.csv", text_column="body")


def test_extract_csv_max_rows(tmp_path: Path):
    inp = tmp_path / "in.csv"
    inp.write_text(
        "id,body\n"
        "1,one\n"
        "2,two\n"
        "3,three\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.csv"
    mock_svc = MagicMock()
    mock_svc.extract_from_text.return_value = SimpleNamespace(
        customer_name="X", contact="", estimated_budget="",
    )
    ok, err = extract_csv_to_csv(
        inp, out, text_column="body", service=mock_svc, max_rows=1,
    )
    assert ok == 1 and err == 0
    assert mock_svc.extract_from_text.call_count == 1
    lines = out.read_text(encoding="utf-8-sig").strip().splitlines()
    assert len(lines) == 2  # header + 1 row


def test_extract_csv_empty_body_counts_error(tmp_path: Path):
    inp = tmp_path / "in.csv"
    # One data row with empty body (quoted empty field)
    inp.write_text('body\n""\n', encoding="utf-8")
    out = tmp_path / "out.csv"
    mock_svc = MagicMock()
    ok, err = extract_csv_to_csv(inp, out, text_column="body", service=mock_svc)
    assert ok == 0 and err == 1
    assert mock_svc.extract_from_text.call_count == 0
