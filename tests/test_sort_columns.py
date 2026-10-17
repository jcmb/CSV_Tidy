from csv_tidy.cleanups.sort_columns import sort_columns_by_name
from csv_tidy.engine import CleanupOptions, run_cleanups
from helpers import make_table


def test_sorts_by_name_case_insensitive() -> None:
    table = make_table(
        ["zebra", "Apple", "banana"],
        [["z", "a", "b"], ["Z", "A", "B"]],
    )
    sorted_table, removed = sort_columns_by_name(table)
    assert removed == []
    assert sorted_table.headers == ["Apple", "banana", "zebra"]
    assert sorted_table.columns[0] == ["a", "A"]
    assert sorted_table.columns[1] == ["b", "B"]
    assert sorted_table.columns[2] == ["z", "Z"]


def test_sort_via_engine() -> None:
    table = make_table(
        ["c", "a", "b"],
        [["3", "1", "2"]],
    )
    result = run_cleanups(table, CleanupOptions(sort_columns=True))
    assert result.table.headers == ["a", "b", "c"]
    assert result.report.sorted_by_name is True
    assert "Sorted remaining columns by name." in result.report.format()


def test_sort_after_removals() -> None:
    table = make_table(
        ["zebra", "notes", "apple"],
        [["z", "", "a"], ["Z", "  ", "A"]],
    )
    result = run_cleanups(
        table,
        CleanupOptions(empty_columns=True, sort_columns=True),
    )
    assert "notes" not in result.table.headers
    assert result.table.headers == ["apple", "zebra"]
