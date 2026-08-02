"""Validation and JSON persistence helpers for the contact book."""

import json
from pathlib import Path
from typing import Any

Contact = dict[str, str]
ContactBook = dict[str, Contact]
DEFAULT_CONTACTS_PATH = Path("contacts.json")


class ContactStorageError(Exception):
    """Raised when contact data cannot be loaded or saved safely."""


def clean_required_text(value: str, field_name: str) -> str:
    """Return stripped, non-empty text for a required field."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError(f"{field_name} cannot be empty")

    return cleaned_value


def _normalize_contact_book(raw_data: Any) -> ContactBook:
    if not isinstance(raw_data, dict):
        raise ContactStorageError("contact data must be a JSON object")

    contacts: ContactBook = {}
    for raw_contact in raw_data.values():
        if not isinstance(raw_contact, dict):
            raise ContactStorageError("each contact must be a JSON object")

        try:
            name = clean_required_text(raw_contact.get("name"), "name")
            phone = clean_required_text(raw_contact.get("phone"), "phone")
            email = raw_contact.get("email", "")
            if not isinstance(email, str):
                raise TypeError("email must be a string")
        except (TypeError, ValueError) as error:
            raise ContactStorageError(f"invalid saved contact: {error}") from error

        contact_key = name.casefold()
        if contact_key in contacts:
            raise ContactStorageError(f"duplicate saved contact: {name}")

        contacts[contact_key] = {
            "name": name,
            "phone": phone,
            "email": email.strip(),
        }

    return contacts


def load_contacts(file_path: str | Path = DEFAULT_CONTACTS_PATH) -> ContactBook:
    """Load and validate contacts from JSON, or return an empty book if absent."""
    path = Path(file_path)
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as contacts_file:
            raw_data = json.load(contacts_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ContactStorageError(f"could not load contacts from {path}") from error
    else:
        return _normalize_contact_book(raw_data)


def save_contacts(
    contacts: ContactBook, file_path: str | Path = DEFAULT_CONTACTS_PATH
) -> None:
    """Validate and write contacts to a readable UTF-8 JSON file."""
    normalized_contacts = _normalize_contact_book(contacts)
    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as contacts_file:
            json.dump(
                normalized_contacts,
                contacts_file,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            contacts_file.write("\n")
    except OSError as error:
        raise ContactStorageError(f"could not save contacts to {path}") from error
