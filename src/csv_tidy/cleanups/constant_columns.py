"""Remove columns where every value is the same."""

from __future__ import annotations

from csv_tidy.cleanups._util import normalize
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table


def remove_constant_columns(table: Table) -> tuple[Table, list[RemovedColumn]]:
    drop: set[int] = set()
    removed: list[RemovedColumn] = []
    for i, header in enumerate(table.headers):
        values = [normalize(v) for v in table.columns[i]]
        if not values:
            # No rows: treat as constant empty
            drop.add(i)
            removed.append(
                RemovedColumn(name=header, reason="constant", details='""', index=i)
            )
            continue
        first = values[0]
        if all(v == first for v in values):
            drop.add(i)
            removed.append(
                RemovedColumn(
                    name=header,
                    reason="constant",
                    details=f'"{first}"',
                    index=i,
                )
            )
    return table.drop_indices(drop), removed
