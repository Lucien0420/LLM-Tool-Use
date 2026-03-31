from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.batch import extract_folder_to_csv


def test_extract_folder_to_csv_mocked(tmp_path: Path):
    inp = tmp_path / "in"
    inp.mkdir()
    (inp / "a.txt").write_text("Name Alice phone 111 budget 3k", encoding="utf-8")
    (inp / "b.txt").write_text("Bob bob@x.com budget 5k", encoding="utf-8")

    out = tmp_path / "out.csv"

    mock_svc = MagicMock()
    mock_svc.extract_from_text.side_effect = [
        SimpleNamespace(customer_name="Alice", contact="111", estimated_budget="3k"),
        SimpleNamespace(customer_name="Bob", contact="bob@x.com", estimated_budget="5k"),
    ]

    ok, err = extract_folder_to_csv(inp, out, service=mock_svc)
    assert ok == 2 and err == 0
    text = out.read_text(encoding="utf-8-sig")
    assert "Alice" in text
    assert "Bob" in text


def test_extract_folder_empty_raises(tmp_path: Path):
    inp = tmp_path / "empty"
    inp.mkdir()
    with pytest.raises(FileNotFoundError):
        extract_folder_to_csv(inp, tmp_path / "o.csv")
