"""Orchestrate selected cleanup passes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from csv_tidy.cleanups import (
    remove_constant_columns,
    remove_duplicate_values,
    remove_duplication_columns,
    remove_email_columns,
    remove_empty_columns,
    remove_id_columns,
    sort_columns_by_name,
)
from csv_tidy.report import RemovalReport, RemovedColumn
from csv_tidy.table import Table

CleanupFn = Callable[[Table], tuple[Table, list[RemovedColumn]]]


@dataclass
class CleanupOptions:
    empty_columns: bool = False
    constant_columns: bool = False
    duplication_columns: bool = False
    remove_ids: bool = False
    duplicate_values: bool = False
    remove_emails: bool = False
    sort_columns: bool = False

    @classmethod
    def all(cls) -> CleanupOptions:
        return cls(
            empty_columns=True,
            constant_columns=True,
            duplication_columns=True,
            remove_ids=True,
            duplicate_values=True,
            remove_emails=True,
            sort_columns=True,
        )

    def any_removal_enabled(self) -> bool:
        return any(
            (
                self.empty_columns,
                self.constant_columns,
                self.duplication_columns,
                self.remove_ids,
                self.duplicate_values,
                self.remove_emails,
            )
        )

    def any_enabled(self) -> bool:
        return self.any_removal_enabled() or self.sort_columns


@dataclass
class CleanupResult:
    table: Table
    report: RemovalReport
    original_headers: list[str] = field(default_factory=list)
    removed_indices_in_original: set[int] = field(default_factory=set)


def run_cleanups(table: Table, options: CleanupOptions) -> CleanupResult:
    """Apply selected cleanups; track which original column indices were removed."""
    original = table.copy()
    surviving: list[int] = list(range(original.column_count))
    current = table.copy()
    all_removed: list[RemovedColumn] = []
    all_notes: list[str] = []

    def _id_pass(tbl: Table) -> tuple[Table, list[RemovedColumn]]:
        next_table, removed, notes = remove_id_columns(tbl)
        all_notes.extend(notes)
        return next_table, removed

    ordered: list[tuple[bool, CleanupFn]] = [
        (options.empty_columns, remove_empty_columns),
        (options.constant_columns, remove_constant_columns),
        (options.duplication_columns, remove_duplication_columns),
        (options.remove_ids, _id_pass),
        (options.duplicate_values, remove_duplicate_values),
        (options.remove_emails, remove_email_columns),
    ]

    for enabled, pass_fn in ordered:
        if not enabled:
            continue
        current, removed = pass_fn(current)
        if not removed:
            continue
        drop_current = {r.index for r in removed if r.index is not None}
        for item in removed:
            if item.index is not None:
                all_removed.append(
                    RemovedColumn(
                        name=item.name,
                        reason=item.reason,
                        details=item.details,
                        index=surviving[item.index],
                    )
                )
            else:
                all_removed.append(item)
        surviving = [
            orig_i
            for cur_i, orig_i in enumerate(surviving)
            if cur_i not in drop_current
        ]

    if options.sort_columns:
        current, _ = sort_columns_by_name(current)

    removed_orig = set(range(original.column_count)) - set(surviving)
    report = RemovalReport(
        removed=all_removed,
        kept_headers=list(current.headers),
        sorted_by_name=options.sort_columns,
        notes=all_notes,
    )
    return CleanupResult(
        table=current,
        report=report,
        original_headers=list(original.headers),
        removed_indices_in_original=removed_orig,
    )


def preview_removed_indices(table: Table, options: CleanupOptions) -> set[int]:
    """Indices in the original table that would be removed under ``options``."""
    return run_cleanups(table, options).removed_indices_in_original
