"""Remove columns with no values."""

from __future__ import annotations

from csv_tidy.cleanups._util import is_empty
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table


def remove_empty_columns(table: Table) -> tuple[Table, list[RemovedColumn]]:
    drop: set[int] = set()
    removed: list[RemovedColumn] = []
    for i, header in enumerate(table.headers):
        values = table.columns[i]
        if all(is_empty(v) for v in values):
            drop.add(i)
            removed.append(
                RemovedColumn(name=header, reason="empty", index=i)
            )
    return table.drop_indices(drop), removed
