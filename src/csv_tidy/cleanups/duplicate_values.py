"""Remove columns with different titles but identical values."""

from __future__ import annotations

from csv_tidy.cleanups._util import normalize
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table


def remove_duplicate_values(table: Table) -> tuple[Table, list[RemovedColumn]]:
    """Keep the leftmost column when values match across differently named columns."""
    drop: set[int] = set()
    removed: list[RemovedColumn] = []
    kept_by_signature: dict[tuple[str, ...], int] = {}

    for i, header in enumerate(table.headers):
        sig = tuple(normalize(v) for v in table.columns[i])
        if sig in kept_by_signature:
            kept_idx = kept_by_signature[sig]
            kept_name = table.headers[kept_idx]
            # Only remove when titles differ (same-title handled by duplication pass)
            if kept_name != header:
                drop.add(i)
                removed.append(
                    RemovedColumn(
                        name=header,
                        reason="duplicate values",
                        details=f'same as "{kept_name}"',
                        index=i,
                    )
                )
            # If titles are the same, leave for / already handled by duplication pass
        else:
            kept_by_signature[sig] = i

    return table.drop_indices(drop), removed
