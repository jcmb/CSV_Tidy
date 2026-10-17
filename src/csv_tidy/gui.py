"""Desktop GUI for CSV_Tidy."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from csv_tidy import __version__
from csv_tidy.cleanups.sort_columns import sort_columns_by_name
from csv_tidy.engine import CleanupOptions, preview_removed_indices, run_cleanups
from csv_tidy.io import Delimiter, default_output_path, load, save
from csv_tidy.table import Table


class CsvTidyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"CSV_Tidy {__version__}")
        self.minsize(1180, 520)
        self.geometry("1280x640")

        self._path: Path | None = None
        self._table: Table | None = None
        self._delimiter = tk.StringVar(value="auto")

        self._opt_empty = tk.BooleanVar(value=True)
        self._opt_constant = tk.BooleanVar(value=True)
        self._opt_duplication = tk.BooleanVar(value=True)
        self._opt_ids = tk.BooleanVar(value=True)
        self._opt_dup_values = tk.BooleanVar(value=True)
        self._opt_emails = tk.BooleanVar(value=True)
        self._opt_sort = tk.BooleanVar(value=True)

        # Column indices excluded from output (click to toggle).
        self._excluded: set[int] = set()
        self._auto_remove: set[int] = set()

        self._build()

    def _build(self) -> None:
        pad = {"padx": 8, "pady": 4}

        top = ttk.Frame(self)
        top.pack(fill=tk.X, **pad)
        ttk.Button(top, text="Open…", command=self._open).pack(side=tk.LEFT)
        self._path_label = ttk.Label(top, text="No file loaded")
        self._path_label.pack(side=tk.LEFT, padx=8)

        delim_frame = ttk.LabelFrame(self, text="Delimiter")
        delim_frame.pack(fill=tk.X, **pad)
        for text, value in (("Auto", "auto"), ("Comma", "comma"), ("Tab", "tab")):
            ttk.Radiobutton(
                delim_frame,
                text=text,
                value=value,
                variable=self._delimiter,
                command=self._reload_if_needed,
            ).pack(side=tk.LEFT, padx=6, pady=4)

        opts = ttk.LabelFrame(self, text="Cleanup options")
        opts.pack(fill=tk.X, **pad)
        opts_row = ttk.Frame(opts)
        opts_row.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(opts_row, text="Select all", command=self._select_all).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        checks = [
            ("Empty Columns", self._opt_empty),
            ("Constant Columns", self._opt_constant),
            ("Duplication Columns", self._opt_duplication),
            ("Remove IDs", self._opt_ids),
            ("Duplicate Values", self._opt_dup_values),
            ("Remove Emails", self._opt_emails),
            ("Sort Columns", self._opt_sort),
        ]
        for text, var in checks:
            command = (
                self._refresh_preview
                if var is self._opt_sort
                else self._on_options_changed
            )
            ttk.Checkbutton(
                opts_row,
                text=text,
                variable=var,
                command=command,
            ).pack(side=tk.LEFT, padx=6)

        preview = ttk.LabelFrame(
            self,
            text="Columns (click to include/exclude; highlighted = excluded)",
        )
        preview.pack(fill=tk.BOTH, expand=True, **pad)
        self._list = tk.Listbox(preview, selectmode=tk.BROWSE, font=("Menlo", 12))
        scroll = ttk.Scrollbar(preview, orient=tk.VERTICAL, command=self._list.yview)
        self._list.configure(yscrollcommand=scroll.set)
        self._list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._list.bind("<ButtonRelease-1>", self._on_column_click)

        report_frame = ttk.LabelFrame(self, text="Report")
        report_frame.pack(fill=tk.BOTH, expand=False, **pad)
        self._report = tk.Text(report_frame, height=8, wrap=tk.WORD)
        self._report.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, **pad)
        ttk.Button(bottom, text="Run / Save…", command=self._run).pack(side=tk.LEFT)
        ttk.Button(bottom, text="Quit", command=self.destroy).pack(side=tk.RIGHT)

    def _cleanup_options(self) -> CleanupOptions:
        # Must not be named _options — that shadows tk.Misc._options used by filedialog.
        return CleanupOptions(
            empty_columns=self._opt_empty.get(),
            constant_columns=self._opt_constant.get(),
            duplication_columns=self._opt_duplication.get(),
            remove_ids=self._opt_ids.get(),
            duplicate_values=self._opt_dup_values.get(),
            remove_emails=self._opt_emails.get(),
            sort_columns=self._opt_sort.get(),
        )

    def _select_all(self) -> None:
        for var in (
            self._opt_empty,
            self._opt_constant,
            self._opt_duplication,
            self._opt_ids,
            self._opt_dup_values,
            self._opt_emails,
            self._opt_sort,
        ):
            var.set(True)
        self._on_options_changed()

    def _delimiter_enum(self) -> Delimiter:
        return Delimiter(self._delimiter.get())

    def _open(self) -> None:
        # macOS Aqua Tk rejects space-separated patterns like "*.csv *.tsv"
        # and often rejects "*.*"; use one pattern per entry and "*".
        path = filedialog.askopenfilename(
            parent=self,
            title="Open CSV or TSV",
            filetypes=[
                ("CSV", "*.csv"),
                ("TSV", "*.tsv"),
                ("All files", "*"),
            ],
        )
        if not path:
            return
        self._path = Path(path)
        self._load_table()

    def _reload_if_needed(self) -> None:
        if self._path is not None:
            self._load_table()

    def _load_table(self) -> None:
        assert self._path is not None
        try:
            self._table = load(self._path, delimiter=self._delimiter_enum())
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Load failed", str(exc))
            return
        self._path_label.configure(text=str(self._path))
        self._recompute_auto_and_reset_exclusions()
        self._refresh_preview()

    def _on_options_changed(self) -> None:
        self._recompute_auto_and_reset_exclusions()
        self._refresh_preview()

    def _recompute_auto_and_reset_exclusions(self) -> None:
        if self._table is None:
            self._auto_remove = set()
            self._excluded = set()
            return
        options = self._cleanup_options()
        self._auto_remove = (
            preview_removed_indices(self._table, options)
            if options.any_removal_enabled()
            else set()
        )
        self._excluded = set(self._auto_remove)

    def _on_column_click(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        if self._table is None:
            return
        selection = self._list.curselection()
        if not selection:
            return
        index = int(selection[0])
        if index < 0 or index >= self._table.column_count:
            return
        if index in self._excluded:
            self._excluded.discard(index)
        else:
            self._excluded.add(index)
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        self._list.delete(0, tk.END)
        if self._table is None:
            self._report.delete("1.0", tk.END)
            return

        for i, header in enumerate(self._table.headers):
            excluded = i in self._excluded
            mark = "✗" if excluded else "✓"
            label = f"{mark} [{i}] {header}"
            self._list.insert(tk.END, label)
            if excluded:
                self._list.itemconfig(i, {"bg": "#f5d0d0", "fg": "#5a1010"})
            else:
                self._list.itemconfig(i, {"bg": "#e8f5e9", "fg": "#1b5e20"})

        self._report.delete("1.0", tk.END)
        self._report.insert("1.0", self._report_text())

    def _cleanup_result(self):
        """Run automatic cleanups for preview reasons/notes."""
        options = self._cleanup_options()
        if self._table is None or not options.any_removal_enabled():
            return None
        return run_cleanups(self._table, options)

    def _auto_reasons(self) -> dict[int, str]:
        """Map original column index → automatic cleanup reason label."""
        result = self._cleanup_result()
        if result is None:
            return {}
        reasons: dict[int, str] = {}
        for item in result.report.removed:
            if item.index is not None:
                reasons[item.index] = item.reason_label()
        return reasons

    def _report_text(self) -> str:
        assert self._table is not None
        lines: list[str] = []
        result = self._cleanup_result()
        auto_reasons = {}
        if result is not None:
            for item in result.report.removed:
                if item.index is not None:
                    auto_reasons[item.index] = item.reason_label()

        if not self._excluded:
            lines.append("Excluded 0 columns from output.")
        else:
            lines.append(f"Excluded {len(self._excluded)} columns from output:")
            for i in sorted(self._excluded):
                name = self._table.headers[i]
                if i in auto_reasons:
                    tag = auto_reasons[i]
                elif i in self._auto_remove:
                    tag = "automatic rule"
                else:
                    tag = "manual exclude"
                lines.append(f"  - [{i}] {name} ({tag})")

        if result is not None and result.report.notes:
            lines.append("Notes:")
            lines.extend(f"  - {note}" for note in result.report.notes)

        kept = self._table.column_count - len(self._excluded)
        lines.append(
            f"Kept {kept} columns, {self._table.row_count} rows."
        )
        if self._opt_sort.get():
            lines.append("Sorted remaining columns by name.")
        lines.append("Click a column to include or exclude it from the output.")
        return "\n".join(lines)

    def _output_table(self) -> Table:
        assert self._table is not None
        cleaned = self._table.drop_indices(self._excluded)
        if self._opt_sort.get():
            cleaned, _ = sort_columns_by_name(cleaned)
        return cleaned

    def _run(self) -> None:
        if self._table is None or self._path is None:
            messagebox.showinfo("CSV_Tidy", "Open a file first.")
            return

        cleaned = self._output_table()
        default = default_output_path(self._path)
        out = filedialog.asksaveasfilename(
            parent=self,
            title="Save cleaned file",
            initialfile=default.name,
            initialdir=str(default.parent),
            defaultextension=default.suffix,
            filetypes=[
                ("CSV", "*.csv"),
                ("TSV", "*.tsv"),
                ("All files", "*"),
            ],
        )
        if not out:
            return
        out_path = Path(out)
        if out_path.resolve() == self._path.resolve():
            if not messagebox.askyesno(
                "Overwrite?",
                f"Overwrite the original file?\n{self._path}",
            ):
                return
        try:
            save(
                cleaned,
                out_path,
                delimiter=self._delimiter_enum()
                if self._delimiter_enum() != Delimiter.AUTO
                else None,
            )
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))
            return

        text = self._report_text() + f"\nWrote {out_path}"
        self._report.delete("1.0", tk.END)
        self._report.insert("1.0", text)
        messagebox.showinfo("CSV_Tidy", f"Wrote {out_path}")


def main() -> None:
    app = CsvTidyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
