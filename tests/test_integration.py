from pathlib import Path

from click.testing import CliRunner

from csv_tidy.cli import main
from csv_tidy.engine import CleanupOptions, run_cleanups
from csv_tidy.io import load


def test_all_cleanups_on_fixture(fixtures_dir: Path) -> None:
    table = load(fixtures_dir / "sample.csv")
    result = run_cleanups(table, CleanupOptions.all())
    # Expected kept: name, Customer Name (notes empty, status constant,
    # Customer ID paired, emails removed, duplicate code/extra values)
    assert "name" in result.table.headers
    assert "Customer Name" in result.table.headers
    assert "notes" not in result.table.headers
    assert "status" not in result.table.headers
    assert "Customer ID" not in result.table.headers
    assert "email" not in result.table.headers
    assert "alt_email" not in result.table.headers
    # one code kept; extra matched code values → dropped
    assert result.table.headers.count("code") == 1
    assert "extra" not in result.table.headers


def test_cli_all_dry_run(fixtures_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(fixtures_dir / "sample.csv"), "--all", "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "Removed" in result.output


def test_cli_writes_output(fixtures_dir: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "cleaned.csv"
    result = runner.invoke(
        main,
        [str(fixtures_dir / "sample.csv"), "--all", "-o", str(out), "-q"],
    )
    assert result.exit_code == 0, result.output
    assert out.is_file()
    cleaned = load(out)
    assert "name" in cleaned.headers
    assert "Customer ID" not in cleaned.headers
