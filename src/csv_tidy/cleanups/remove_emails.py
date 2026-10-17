"""Remove columns whose non-empty values are all email addresses."""

from __future__ import annotations

import re

from csv_tidy.cleanups._util import is_empty
from csv_tidy.report import RemovedColumn
from csv_tidy.table import Table

# Practical local@domain with a dot in the domain
_EMAIL = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def _is_email(value: str) -> bool:
    return bool(_EMAIL.match(value.strip()))


def remove_email_columns(table: Table) -> tuple[Table, list[RemovedColumn]]:
    drop: set[int] = set()
    removed: list[RemovedColumn] = []

    for i, header in enumerate(table.headers):
        non_empty = [v for v in table.columns[i] if not is_empty(v)]
        if not non_empty:
            continue
        if all(_is_email(v) for v in non_empty):
            drop.add(i)
            removed.append(
                RemovedColumn(name=header, reason="email addresses", index=i)
            )

    return table.drop_indices(drop), removed
