from csv_tidy.cleanups.remove_emails import remove_email_columns
from helpers import make_table


def test_removes_email_column() -> None:
    table = make_table(
        ["name", "email"],
        [["Ada", "ada@example.com"], ["Grace", "grace@example.org"]],
    )
    cleaned, removed = remove_email_columns(table)
    assert cleaned.headers == ["name"]
    assert removed[0].reason == "email addresses"


def test_ignores_empty_cells() -> None:
    table = make_table(
        ["email"],
        [["ada@example.com"], [""], ["  "], ["bob@x.co.uk"]],
    )
    cleaned, removed = remove_email_columns(table)
    assert cleaned.headers == []
    assert len(removed) == 1


def test_mixed_not_removed() -> None:
    table = make_table(
        ["contact"],
        [["ada@example.com"], ["not-an-email"]],
    )
    cleaned, removed = remove_email_columns(table)
    assert cleaned.headers == ["contact"]
    assert removed == []


def test_all_empty_not_treated_as_email() -> None:
    table = make_table(["e"], [["",], ["  ",]])
    cleaned, removed = remove_email_columns(table)
    assert cleaned.headers == ["e"]
    assert removed == []
