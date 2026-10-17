"""Load and save CSV/TSV files."""

from __future__ import annotations

import csv
from enum import Enum
from pathlib import Path

from csv_tidy.table import Table


class Delimiter(str, Enum):
    AUTO = "auto"
    COMMA = "comma"
    TAB = "tab"


_DELIMITER_CHAR = {
    Delimiter.COMMA: ",",
    Delimiter.TAB: "\t",
}


def delimiter_from_path(path: Path) -> Delimiter:
    if path.suffix.lower() == ".tsv":
        return Delimiter.TAB
    return Delimiter.COMMA


def resolve_delimiter(path: Path, choice: Delimiter, sample: str | None = None) -> str:
    if choice == Delimiter.AUTO:
        if sample is not None:
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
                return dialect.delimiter
            except csv.Error:
                pass
        return _DELIMITER_CHAR[delimiter_from_path(path)]
    return _DELIMITER_CHAR[choice]


def default_output_path(input_path: Path) -> Path:
    delim = delimiter_from_path(input_path)
    ext = ".tsv" if delim == Delimiter.TAB else ".csv"
    return input_path.with_name(f"{input_path.stem}_tidy{ext}")


def load(path: Path | str, delimiter: Delimiter = Delimiter.AUTO) -> Table:
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    if not text.strip():
        return Table()

    sample = text[:8192]
    delim_char = resolve_delimiter(path, delimiter, sample=sample)
    reader = csv.reader(text.splitlines(), delimiter=delim_char)
    rows = list(reader)
    if not rows:
        return Table()

    headers = [h if h is not None else "" for h in rows[0]]
    width = len(headers)
    columns: list[list[str]] = [[] for _ in range(width)]

    for row in rows[1:]:
        # Pad or trim to header width
        padded = list(row) + [""] * max(0, width - len(row))
        padded = padded[:width]
        for i, cell in enumerate(padded):
            columns[i].append("" if cell is None else str(cell))

    return Table(headers=headers, columns=columns)


def save(
    table: Table,
    path: Path | str,
    delimiter: Delimiter | None = None,
) -> None:
    path = Path(path)
    if delimiter is None or delimiter == Delimiter.AUTO:
        delim_char = _DELIMITER_CHAR[delimiter_from_path(path)]
    else:
        delim_char = _DELIMITER_CHAR[delimiter]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter=delim_char)
        writer.writerow(table.headers)
        for r in range(table.row_count):
            writer.writerow([table.columns[c][r] for c in range(table.column_count)])
