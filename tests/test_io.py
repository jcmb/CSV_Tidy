from pathlib import Path

from csv_tidy.io import Delimiter, default_output_path, load, save


def test_load_csv(fixtures_dir: Path) -> None:
    table = load(fixtures_dir / "sample.csv")
    assert "name" in table.headers
    assert table.row_count == 2


def test_load_tsv(fixtures_dir: Path) -> None:
    table = load(fixtures_dir / "sample.tsv", delimiter=Delimiter.TAB)
    assert table.headers == ["id", "label", "blank"]
    assert table.row_count == 2


def test_roundtrip(tmp_path: Path) -> None:
    src = tmp_path / "in.csv"
    src.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    table = load(src)
    out = tmp_path / "out.csv"
    save(table, out)
    again = load(out)
    assert again.headers == ["a", "b"]
    assert again.columns == [["1", "3"], ["2", "4"]]


def test_default_output_path() -> None:
    assert default_output_path(Path("data.csv")).name == "data_tidy.csv"
    assert default_output_path(Path("data.tsv")).name == "data_tidy.tsv"
