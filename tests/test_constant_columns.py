from csv_tidy.cleanups.constant_columns import remove_constant_columns
from helpers import make_table


def test_removes_constant() -> None:
    table = make_table(
        ["vary", "status"],
        [["a", "active"], ["b", "active"]],
    )
    cleaned, removed = remove_constant_columns(table)
    assert cleaned.headers == ["vary"]
    assert removed[0].name == "status"
    assert '"active"' in removed[0].details


def test_all_empty_is_constant_when_empty_pass_off() -> None:
    table = make_table(["blank"], [["",], ["  ",]])
    cleaned, removed = remove_constant_columns(table)
    assert cleaned.headers == []
    assert len(removed) == 1
