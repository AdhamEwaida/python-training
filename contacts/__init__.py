"""Persistent contact-book package."""

from contacts.manager import (
    add_contact,
    compare_contact_names,
    list_contacts,
    run_cli,
    search_by_name,
    search_by_phone,
)
from contacts.utils import (
    Contact,
    ContactBook,
    ContactStorageError,
    load_contacts,
    save_contacts,
)

__all__ = [
    "Contact",
    "ContactBook",
    "ContactStorageError",
    "add_contact",
    "compare_contact_names",
    "list_contacts",
    "load_contacts",
    "run_cli",
    "save_contacts",
    "search_by_name",
    "search_by_phone",
]
