"""Command-line interface for CSV_Tidy."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from csv_tidy import __version__
from csv_tidy.engine import CleanupOptions, run_cleanups
from csv_tidy.io import Delimiter, default_output_path, load, save


def _build_options(
    all_opts: bool,
    empty_columns: bool,
    constant_columns: bool,
    duplication_columns: bool,
    remove_ids: bool,
    duplicate_values: bool,
    remove_emails: bool,
    sort_columns: bool,
) -> CleanupOptions:
    if all_opts:
        return CleanupOptions.all()
    return CleanupOptions(
        empty_columns=empty_columns,
        constant_columns=constant_columns,
        duplication_columns=duplication_columns,
        remove_ids=remove_ids,
        duplicate_values=duplicate_values,
        remove_emails=remove_emails,
        sort_columns=sort_columns,
    )


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: {stem}_tidy.csv|tsv).",
)
@click.option(
    "--delimiter",
    type=click.Choice(["auto", "comma", "tab"], case_sensitive=False),
    default="auto",
    show_default=True,
    help="Field delimiter.",
)
@click.option("--empty-columns", is_flag=True, help="Remove empty columns.")
@click.option("--constant-columns", is_flag=True, help="Remove constant columns.")
@click.option(
    "--duplication-columns",
    is_flag=True,
    help="Remove columns with the same title and values.",
)
@click.option("--remove-ids", is_flag=True, help="Remove ID columns paired with Name.")
@click.option(
    "--duplicate-values",
    is_flag=True,
    help="Remove differently named columns with identical values.",
)
@click.option("--remove-emails", is_flag=True, help="Remove email-address columns.")
@click.option(
    "--sort-columns",
    is_flag=True,
    help="Sort remaining columns alphabetically by name.",
)
@click.option("--all", "all_opts", is_flag=True, help="Enable every cleanup.")
@click.option("--dry-run", is_flag=True, help="Print report only; do not write.")
@click.option(
    "--force",
    is_flag=True,
    help="Allow overwriting the input file when output matches input.",
)
@click.option("-q", "--quiet", is_flag=True, help="Suppress report output.")
@click.version_option(__version__, prog_name="csv-tidy")
def main(
    input_path: Path,
    output_path: Path | None,
    delimiter: str,
    empty_columns: bool,
    constant_columns: bool,
    duplication_columns: bool,
    remove_ids: bool,
    duplicate_values: bool,
    remove_emails: bool,
    sort_columns: bool,
    all_opts: bool,
    dry_run: bool,
    force: bool,
    quiet: bool,
) -> None:
    """Clean up a CSV or TSV file by removing unhelpful columns."""
    options = _build_options(
        all_opts,
        empty_columns,
        constant_columns,
        duplication_columns,
        remove_ids,
        duplicate_values,
        remove_emails,
        sort_columns,
    )
    if not options.any_enabled():
        raise click.UsageError(
            "Select at least one cleanup option, or use --all."
        )

    delim = Delimiter(delimiter.lower())
    try:
        table = load(input_path, delimiter=delim)
    except OSError as exc:
        raise click.ClickException(f"Could not read {input_path}: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 — surface parse errors cleanly
        raise click.ClickException(f"Could not parse {input_path}: {exc}") from exc

    result = run_cleanups(table, options)

    if not quiet:
        click.echo(result.report.format())
        click.echo(f"Kept {result.table.column_count} columns, {result.table.row_count} rows.")

    if dry_run:
        return

    out = output_path or default_output_path(input_path)
    if out.resolve() == input_path.resolve() and not force:
        raise click.UsageError(
            f"Refusing to overwrite input {input_path}; pass --force to allow."
        )

    try:
        save(result.table, out, delimiter=delim if delim != Delimiter.AUTO else None)
    except OSError as exc:
        raise click.ClickException(f"Could not write {out}: {exc}") from exc

    if not quiet:
        click.echo(f"Wrote {out}")


if __name__ == "__main__":
    main(standalone_mode=True)
    sys.exit(0)
