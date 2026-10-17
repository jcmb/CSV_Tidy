"""In-memory columnar table (supports duplicate header names)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Table:
    """Column-oriented table. ``columns[i]`` holds values for ``headers[i]``."""

    headers: list[str] = field(default_factory=list)
    columns: list[list[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.headers) != len(self.columns):
            raise ValueError("headers and columns must have the same length")
        if self.columns:
            lengths = {len(c) for c in self.columns}
            if len(lengths) > 1:
                raise ValueError("all columns must have the same number of rows")

    @property
    def row_count(self) -> int:
        return len(self.columns[0]) if self.columns else 0

    @property
    def column_count(self) -> int:
        return len(self.headers)

    def copy(self) -> Table:
        return Table(
            headers=list(self.headers),
            columns=[list(col) for col in self.columns],
        )

    def drop_indices(self, indices: set[int]) -> Table:
        """Return a new table without the given column indices."""
        keep = [i for i in range(len(self.headers)) if i not in indices]
        return Table(
            headers=[self.headers[i] for i in keep],
            columns=[self.columns[i] for i in keep],
        )

    def column_values(self, index: int) -> list[str]:
        return self.columns[index]
