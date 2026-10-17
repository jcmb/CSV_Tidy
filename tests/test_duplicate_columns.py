from csv_tidy.cleanups.duplicate_columns import remove_duplication_columns
from helpers import make_table


def test_same_title_same_values() -> None:
    table = make_table(
        ["code", "code", "other"],
        [["A", "A", "1"], ["B", "B", "2"]],
    )
    cleaned, removed = remove_duplication_columns(table)
    assert cleaned.headers == ["code", "other"]
    assert len(removed) == 1
    assert removed[0].name == "code"


def test_same_title_different_values_kept() -> None:
    table = make_table(
        ["code", "code"],
        [["A", "X"], ["B", "Y"]],
    )
    cleaned, removed = remove_duplication_columns(table)
    assert cleaned.headers == ["code", "code"]
    assert removed == []
