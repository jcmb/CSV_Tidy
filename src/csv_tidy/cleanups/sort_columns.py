"""Sort columns alphabetically by header name."""

from __future__ import annotations

from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table


def sort_columns_by_name(table: Table) -> tuple[Table, list[RemovedColumn]]:
    """Return a new table with columns sorted by header (case-insensitive).

    Stable for equal names (original order preserved as a tiebreaker).
    Does not remove any columns.
    """
    order = sorted(
        range(table.column_count),
        key=lambda i: (table.headers[i].casefold(), i),
    )
    return (
        Table(
            headers=[table.headers[i] for i in order],
            columns=[table.columns[i] for i in order],
        ),
        [],
    )
