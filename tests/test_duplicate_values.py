from csv_tidy.cleanups.duplicate_values import remove_duplicate_values
from helpers import make_table


def test_different_titles_same_values() -> None:
    table = make_table(
        ["email", "alt_email", "name"],
        [
            ["a@x.com", "a@x.com", "Ada"],
            ["b@x.com", "b@x.com", "Bob"],
        ],
    )
    cleaned, removed = remove_duplicate_values(table)
    assert cleaned.headers == ["email", "name"]
    assert removed[0].name == "alt_email"
    assert "email" in removed[0].details


def test_same_title_not_removed_here() -> None:
    table = make_table(
        ["code", "code"],
        [["A", "A"], ["B", "B"]],
    )
    cleaned, removed = remove_duplicate_values(table)
    assert cleaned.headers == ["code", "code"]
    assert removed == []
