from csv_tidy.cleanups.empty_columns import remove_empty_columns
from helpers import make_table


def test_removes_all_empty_column() -> None:
    table = make_table(
        ["a", "empty", "b"],
        [["1", "", "x"], ["2", "  ", "y"]],
    )
    cleaned, removed = remove_empty_columns(table)
    assert cleaned.headers == ["a", "b"]
    assert [r.name for r in removed] == ["empty"]


def test_keeps_partially_filled() -> None:
    table = make_table(["a"], [["",], ["x",]])
    cleaned, removed = remove_empty_columns(table)
    assert cleaned.headers == ["a"]
    assert removed == []
