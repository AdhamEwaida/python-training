import pytest

from contact_book import (
    add_contact,
    compare_contact_names,
    list_contacts,
    run_cli,
    search_by_name,
    search_by_phone,
)


def test_add_contact_stores_nested_contact_data():
    contacts = {}

    add_contact(contacts, "  Adham  ", " 0590000000 ", " adham@example.com ")

    assert contacts == {
        "adham": {
            "name": "Adham",
            "phone": "0590000000",
            "email": "adham@example.com",
        }
    }


def test_search_by_name_is_case_insensitive():
    contacts = {}
    add_contact(contacts, "Adham", "0590000000")

    assert search_by_name(contacts, "ADHAM") == {
        "name": "Adham",
        "phone": "0590000000",
        "email": "",
    }


def test_search_by_name_returns_a_copy():
    contacts = {}
    add_contact(contacts, "Adham", "0590000000")

    result = search_by_name(contacts, "Adham")
    result["phone"] = "changed"

    assert contacts["adham"]["phone"] == "0590000000"


def test_add_contact_rejects_duplicate_normalized_name():
    contacts = {}
    add_contact(contacts, "Adham", "0590000000")

    with pytest.raises(ValueError, match="already exists"):
        add_contact(contacts, " adHAM ", "0591111111")


def test_search_by_phone_returns_matching_contact():
    contacts = {}
    add_contact(contacts, "Adham", "0590000000")
    add_contact(contacts, "Lina", "0591111111")

    assert search_by_phone(contacts, "0591111111") == {
        "name": "Lina",
        "phone": "0591111111",
        "email": "",
    }


def test_search_functions_return_none_when_contact_is_missing():
    contacts = {}
    add_contact(contacts, "Adham", "0590000000")

    assert search_by_name(contacts, "Lina") is None
    assert search_by_phone(contacts, "0599999999") is None


def test_list_contacts_returns_alphabetically_sorted_copies():
    contacts = {}
    add_contact(contacts, "Zaid", "3")
    add_contact(contacts, "adham", "1")
    add_contact(contacts, "Mona", "2")

    listed_contacts = list_contacts(contacts)

    assert [contact["name"] for contact in listed_contacts] == [
        "adham",
        "Mona",
        "Zaid",
    ]
    listed_contacts[0]["phone"] = "changed"
    assert contacts["adham"]["phone"] == "1"


def test_compare_contact_names_returns_union_and_intersection():
    first = {}
    second = {}
    add_contact(first, "Adham", "1")
    add_contact(first, "Lina", "2")
    add_contact(second, "ADHAM", "3")
    add_contact(second, "Omar", "4")

    all_names, shared_names = compare_contact_names(first, second)

    assert all_names == {"adham", "lina", "omar"}
    assert shared_names == {"adham"}


@pytest.mark.parametrize(
    ("name", "phone", "email", "error_type"),
    [
        ("", "0590000000", "", ValueError),
        ("   ", "0590000000", "", ValueError),
        ("Adham", "", "", ValueError),
        (None, "0590000000", "", TypeError),
        ("Adham", None, "", TypeError),
        ("Adham", "0590000000", None, TypeError),
    ],
)
def test_add_contact_rejects_invalid_fields(name, phone, email, error_type):
    with pytest.raises(error_type):
        add_contact({}, name, phone, email)


@pytest.mark.parametrize("search_term", ["", "   ", None])
def test_search_functions_reject_invalid_search_terms(search_term):
    error_type = TypeError if search_term is None else ValueError

    with pytest.raises(error_type):
        search_by_name({}, search_term)

    with pytest.raises(error_type):
        search_by_phone({}, search_term)


def test_run_cli_can_exit(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "5")

    run_cli()

    assert "Goodbye." in capsys.readouterr().out
