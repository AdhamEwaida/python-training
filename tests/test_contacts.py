import json

import pytest

from contacts.manager import add_contact, run_cli
from contacts.utils import ContactStorageError, load_contacts, save_contacts
from passwords import WeakPasswordError, strong_password


def test_contacts_round_trip_through_json(tmp_path):
    contacts = {}
    add_contact(contacts, "Adham", "0590000000", "adham@example.com")
    file_path = tmp_path / "contacts.json"

    save_contacts(contacts, file_path)

    assert load_contacts(file_path) == contacts
    saved_data = json.loads(file_path.read_text(encoding="utf-8"))
    assert saved_data["adham"]["name"] == "Adham"


def test_load_contacts_returns_empty_book_when_file_is_missing(tmp_path):
    assert load_contacts(tmp_path / "missing.json") == {}


def test_load_contacts_normalizes_saved_keys(tmp_path):
    file_path = tmp_path / "contacts.json"
    file_path.write_text(
        json.dumps(
            {
                "WRONG KEY": {
                    "name": "  Adham  ",
                    "phone": " 0590000000 ",
                    "email": " adham@example.com ",
                }
            }
        ),
        encoding="utf-8",
    )

    assert load_contacts(file_path) == {
        "adham": {
            "name": "Adham",
            "phone": "0590000000",
            "email": "adham@example.com",
        }
    }


@pytest.mark.parametrize("invalid_content", ["not json", "[]", '{"a": 1}'])
def test_load_contacts_rejects_invalid_saved_data(tmp_path, invalid_content):
    file_path = tmp_path / "contacts.json"
    file_path.write_text(invalid_content, encoding="utf-8")

    with pytest.raises(ContactStorageError):
        load_contacts(file_path)


def test_cli_adds_and_persists_a_contact(tmp_path, monkeypatch, capsys):
    answers = iter(["1", "Adham", "0590000000", "", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    file_path = tmp_path / "contacts.json"

    exit_code = run_cli(file_path)

    assert exit_code == 0
    assert load_contacts(file_path)["adham"]["phone"] == "0590000000"
    assert "Contact added and saved." in capsys.readouterr().out


def test_cli_reports_corrupt_storage_and_returns_failure(tmp_path, capsys):
    file_path = tmp_path / "contacts.json"
    file_path.write_text("invalid", encoding="utf-8")

    exit_code = run_cli(file_path)

    assert exit_code == 1
    assert "could not load contacts" in capsys.readouterr().out


@pytest.mark.parametrize(
    "password",
    [
        "Strong1!",
        "LONG PASSWORD 2#",
        "Abcdef3_",
    ],
)
def test_strong_password_accepts_valid_passwords(password):
    assert strong_password(password) is True


@pytest.mark.parametrize(
    ("password", "missing_requirement"),
    [
        ("Short1!", "at least 8 characters"),
        ("lowercase1!", "an uppercase letter"),
        ("NoNumber!", "a number"),
        ("NoSpecial1", "a special character"),
        ("Password1 ", "a special character"),
        ("", "at least 8 characters"),
    ],
)
def test_strong_password_raises_for_weak_passwords(password, missing_requirement):
    with pytest.raises(WeakPasswordError, match=missing_requirement):
        strong_password(password)


@pytest.mark.parametrize("password", [None, 12345678, True])
def test_strong_password_rejects_non_string_values(password):
    with pytest.raises(TypeError, match="must be a string"):
        strong_password(password)
