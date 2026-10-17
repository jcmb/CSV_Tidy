"""Removal report types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RemovedColumn:
    name: str
    reason: str
    details: str = ""
    index: int | None = None

    def reason_label(self) -> str:
        if self.details:
            return f"{self.reason}: {self.details}"
        return self.reason

    def format_line(self) -> str:
        return f"  - {self.name} ({self.reason_label()})"


@dataclass
class RemovalReport:
    removed: list[RemovedColumn] = field(default_factory=list)
    kept_headers: list[str] = field(default_factory=list)
    sorted_by_name: bool = False
    notes: list[str] = field(default_factory=list)

    def format(self) -> str:
        if not self.removed:
            lines = ["Removed 0 columns."]
        else:
            lines = [f"Removed {len(self.removed)} columns:"]
            lines.extend(item.format_line() for item in self.removed)
        if self.notes:
            lines.append("Notes:")
            lines.extend(f"  - {note}" for note in self.notes)
        if self.sorted_by_name:
            lines.append("Sorted remaining columns by name.")
        return "\n".join(lines)
