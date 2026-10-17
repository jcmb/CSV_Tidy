"""Remove columns with the same title and the same values."""

from __future__ import annotations

from collections import defaultdict

from csv_tidy.cleanups._util import normalize
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table


def remove_duplication_columns(table: Table) -> tuple[Table, list[RemovedColumn]]:
    """Keep the first column in each same-title group when values match."""
    groups: dict[str, list[int]] = defaultdict(list)
    for i, header in enumerate(table.headers):
        groups[header].append(i)

    drop: set[int] = set()
    removed: list[RemovedColumn] = []

    for header, indices in groups.items():
        if len(indices) < 2:
            continue
        # Among identical-value siblings, keep the leftmost
        kept_by_signature: dict[tuple[str, ...], int] = {}
        for idx in indices:
            sig = tuple(normalize(v) for v in table.columns[idx])
            if sig in kept_by_signature:
                drop.add(idx)
                kept = table.headers[kept_by_signature[sig]]
                removed.append(
                    RemovedColumn(
                        name=header,
                        reason="duplication",
                        details=f'duplicate of column "{kept}"',
                        index=idx,
                    )
                )
            else:
                kept_by_signature[sig] = idx

    return table.drop_indices(drop), removed
