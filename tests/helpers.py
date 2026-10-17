from __future__ import annotations

from csv_tidy.table import Table


def make_table(headers: list[str], rows: list[list[str]]) -> Table:
    columns: list[list[str]] = [[] for _ in headers]
    for row in rows:
        for i, cell in enumerate(row):
            columns[i].append(cell)
    return Table(headers=headers, columns=columns)
