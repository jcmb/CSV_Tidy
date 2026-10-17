from csv_tidy.cleanups.remove_ids import remove_id_columns
from helpers import make_table


def test_removes_matching_id() -> None:
    table = make_table(
        ["Customer ID", "Customer Name", "x"],
        [["1", "Ada", "a"], ["2", "Grace", "b"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Customer Name", "x"]
    assert removed[0].name == "Customer ID"
    assert "Customer Name" in removed[0].reason


def test_case_insensitive() -> None:
    table = make_table(
        ["customer id", "CUSTOMER name"],
        [["1", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["CUSTOMER name"]
    assert len(removed) == 1


def test_unmatched_id_stays() -> None:
    table = make_table(
        ["Order ID", "Customer Name"],
        [["9", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Order ID", "Customer Name"]
    assert removed == []


def test_removes_user_id_paired_with_value() -> None:
    table = make_table(
        ["Assignee", "Assignee User ID", "note"],
        [["Ada", "1", "a"], ["Grace", "2", "b"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Assignee", "note"]
    assert removed[0].name == "Assignee User ID"
    assert "Assignee" in removed[0].reason


def test_user_id_case_insensitive() -> None:
    table = make_table(
        ["owner", "Owner User ID"],
        [["Ada", "9"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["owner"]
    assert len(removed) == 1


def test_unmatched_user_id_stays() -> None:
    table = make_table(
        ["Assignee User ID", "Reporter"],
        [["1", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Assignee User ID", "Reporter"]
    assert removed == []


def test_user_id_falls_back_to_name_pair() -> None:
    table = make_table(
        ["Foo User ID", "Foo User Name"],
        [["1", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Foo User Name"]
    assert removed[0].name == "Foo User ID"


def test_removes_code_paired_with_meaning() -> None:
    table = make_table(
        ["Status Code", "Status Meaning", "x"],
        [["01", "Open", "a"], ["02", "Closed", "b"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Status Meaning", "x"]
    assert removed[0].name == "Status Code"
    assert "Status Meaning" in removed[0].reason


def test_code_meaning_case_insensitive() -> None:
    table = make_table(
        ["priority code", "PRIORITY meaning"],
        [["1", "High"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["PRIORITY meaning"]
    assert len(removed) == 1


def test_unmatched_code_stays() -> None:
    table = make_table(
        ["Status Code", "Other Meaning"],
        [["01", "Open"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Status Code", "Other Meaning"]
    assert removed == []


def test_removes_code_paired_with_name() -> None:
    table = make_table(
        ["Type Code", "Type Name"],
        [["A", "Alpha"], ["B", "Beta"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Type Name"]
    assert removed[0].name == "Type Code"


def test_removes_id_paired_with_meaning() -> None:
    table = make_table(
        ["Status ID", "Status Meaning"],
        [["1", "Open"], ["2", "Closed"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Status Meaning"]
    assert removed[0].name == "Status ID"


def test_prefers_meaning_over_name_for_code() -> None:
    table = make_table(
        ["Status Code", "Status Name", "Status Meaning"],
        [["1", "n1", "Open"], ["2", "n2", "Closed"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert "Status Code" not in cleaned.headers
    assert "Status Meaning" in cleaned.headers
    assert removed[0].name == "Status Code"
    assert "Status Meaning" in removed[0].reason


def test_keeps_id_when_same_id_maps_to_different_names() -> None:
    table = make_table(
        ["Customer ID", "Customer Name"],
        [["1", "Ada"], ["1", "Grace"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Customer ID", "Customer Name"]
    assert removed == []


def test_removes_id_when_same_name_maps_to_different_ids() -> None:
    # One-way check: ID→name is fine even if names collide across IDs.
    table = make_table(
        ["Customer ID", "Customer Name"],
        [["1", "Ada"], ["2", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Customer Name"]
    assert len(removed) == 1


def test_removes_user_id_when_same_display_has_different_ids() -> None:
    table = make_table(
        ["Assignee", "Assignee User ID"],
        [["Ada", "1"], ["Ada", "2"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Assignee"]
    assert removed[0].name == "Assignee User ID"


def test_keeps_code_when_same_code_maps_to_different_meanings() -> None:
    table = make_table(
        ["Status Code", "Status Meaning"],
        [["01", "Open"], ["01", "Closed"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Status Code", "Status Meaning"]
    assert removed == []


def test_allows_repeated_consistent_pairs() -> None:
    table = make_table(
        ["Customer ID", "Customer Name"],
        [["1", "Ada"], ["2", "Grace"], ["1", "Ada"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Customer Name"]
    assert len(removed) == 1


def test_order_created_by_user_id() -> None:
    table = make_table(
        ["Order Created By User ID", "Order Created By", "x"],
        [["101", "Ada Lovelace", "a"], ["202", "Grace Hopper", "b"], ["101", "Ada Lovelace", "c"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Order Created By", "x"]
    assert removed[0].name == "Order Created By User ID"
    assert "Order Created By" in removed[0].reason


def test_org_id_pairs_with_organization_name() -> None:
    table = make_table(
        ["Ship From Org ID", "Ship From Organization Name", "x"],
        [["10", "Acme", "a"], ["20", "Beta", "b"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Ship From Organization Name", "x"]
    assert removed[0].name == "Ship From Org ID"
    assert "Ship From Organization Name" in removed[0].reason


def test_price_list_id_pairs_with_bare_prefix() -> None:
    table = make_table(
        ["Price List", "Price List ID", "x"],
        [["Retail", "1", "a"], ["Wholesale", "2", "b"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Price List", "x"]
    assert removed[0].name == "Price List ID"
    assert "Price List" in removed[0].reason


def test_sales_rep_id_pairs_with_bare_prefix() -> None:
    table = make_table(
        ["Sales Rep ID", "Sales Rep"],
        [["9", "Ada"], ["8", "Grace"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Sales Rep"]
    assert removed[0].name == "Sales Rep ID"


def test_prefers_name_over_bare_prefix_for_id() -> None:
    table = make_table(
        ["Customer", "Customer ID", "Customer Name"],
        [["skip", "1", "Ada"], ["skip", "2", "Grace"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Customer", "Customer Name"]
    assert removed[0].name == "Customer ID"
    assert "Customer Name" in removed[0].reason


def test_contact_id_pairs_with_contact_name() -> None:
    table = make_table(
        ["Contact name", "Contact ID"],
        [["Ada", "1"], ["Grace", "2"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Contact name"]
    assert removed[0].name == "Contact ID"
    assert "Contact name" in removed[0].reason


def test_code_pairs_with_desc() -> None:
    table = make_table(
        ["Bill To Sales Channel Code", "Bill To Sales Channel Desc"],
        [["WEB", "Web Store"], ["RET", "Retail"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Bill To Sales Channel Desc"]
    assert removed[0].name == "Bill To Sales Channel Code"
    assert "Bill To Sales Channel Desc" in removed[0].reason


def test_booked_by_user_id() -> None:
    table = make_table(
        ["Booked By", "Booked By User ID"],
        [["Ada", "1"], ["Grace", "2"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Booked By"]
    assert removed[0].name == "Booked By User ID"
    assert "Booked By" in removed[0].reason


def test_customer_number_pairs_with_bare_prefix() -> None:
    table = make_table(
        ["Invoice To Customer", "Invoice To Customer Number"],
        [["Acme", "1001"], ["Beta", "1002"]],
    )
    cleaned, removed, _notes = remove_id_columns(table)
    assert cleaned.headers == ["Invoice To Customer"]
    assert removed[0].name == "Invoice To Customer Number"
    assert "Invoice To Customer" in removed[0].reason


def test_ship_to_contact_id_name() -> None:
    table = make_table(
        ["Ship To Contact ID", "Ship To Contact Name"],
        [["1", "Ada"], ["2", "Grace"]],
    )
    cleaned, removed, notes = remove_id_columns(table)
    assert cleaned.headers == ["Ship To Contact Name"]
    assert removed[0].name == "Ship To Contact ID"
    assert notes == []


def test_ship_to_contact_inconsistent_keeps_and_notes() -> None:
    table = make_table(
        ["Ship To Contact ID", "Ship To Contact Name"],
        [["1", "Ada"], ["1", "Grace"]],
    )
    cleaned, removed, notes = remove_id_columns(table)
    assert cleaned.headers == ["Ship To Contact ID", "Ship To Contact Name"]
    assert removed == []
    assert any("Ship To Contact ID" in n and "inconsistent" in n for n in notes)
