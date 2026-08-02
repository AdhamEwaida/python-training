"""Contact-book operations and command-line interface."""

from pathlib import Path

from contacts.utils import (
    DEFAULT_CONTACTS_PATH,
    Contact,
    ContactBook,
    ContactStorageError,
    clean_required_text,
    load_contacts,
    save_contacts,
)


def add_contact(contacts: ContactBook, name: str, phone: str, email: str = "") -> None:
    """Add a contact, using a normalized name as the dictionary key."""
    cleaned_name = clean_required_text(name, "name")
    cleaned_phone = clean_required_text(phone, "phone")

    if not isinstance(email, str):
        raise TypeError("email must be a string")

    contact_key = cleaned_name.casefold()
    if contact_key in contacts:
        raise ValueError(f"contact '{cleaned_name}' already exists")

    contacts[contact_key] = {
        "name": cleaned_name,
        "phone": cleaned_phone,
        "email": email.strip(),
    }


def search_by_name(contacts: ContactBook, name: str) -> Contact | None:
    """Find a contact by name in average O(1) time."""
    cleaned_name = clean_required_text(name, "name")
    contact = contacts.get(cleaned_name.casefold())
    return contact.copy() if contact else None


def search_by_phone(contacts: ContactBook, phone: str) -> Contact | None:
    """Find a contact by scanning phone numbers in O(n) time."""
    cleaned_phone = clean_required_text(phone, "phone")

    for contact in contacts.values():
        if contact.get("phone") == cleaned_phone:
            return contact.copy()

    return None


def list_contacts(contacts: ContactBook) -> list[Contact]:
    """Return contact copies sorted by name."""
    return [
        contact.copy()
        for contact in sorted(
            contacts.values(), key=lambda item: item.get("name", "").casefold()
        )
    ]


def compare_contact_names(
    first: ContactBook, second: ContactBook
) -> tuple[set[str], set[str]]:
    """Return the union and intersection of normalized contact-name sets."""
    first_names = set(first)
    second_names = set(second)
    return first_names | second_names, first_names & second_names


def _display_contact(contact: Contact | None) -> None:
    if contact is None:
        print("Contact not found.")
        return

    print(f"Name: {contact.get('name', '')}")
    print(f"Phone: {contact.get('phone', '')}")
    print(f"Email: {contact.get('email', '') or '-'}")


def run_cli(file_path: str | Path = DEFAULT_CONTACTS_PATH) -> int:
    """Run the persistent command-line contact book."""
    try:
        contacts = load_contacts(file_path)
    except ContactStorageError as error:
        print(f"Error: {error}")
        return 1

    while True:
        print("\nContact Book")
        print("1. Add contact")
        print("2. Search by name")
        print("3. Search by phone")
        print("4. List contacts")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_contact(
                    contacts,
                    input("Name: "),
                    input("Phone: "),
                    input("Email (optional): "),
                )
                save_contacts(contacts, file_path)
            elif choice == "2":
                _display_contact(search_by_name(contacts, input("Name: ")))
            elif choice == "3":
                _display_contact(search_by_phone(contacts, input("Phone: ")))
            elif choice == "4":
                saved_contacts = list_contacts(contacts)
                if not saved_contacts:
                    print("No contacts saved.")
                    continue

                for contact in saved_contacts:
                    print()
                    _display_contact(contact)
            elif choice == "5":
                print("Goodbye.")
                return 0
            else:
                print("Invalid option.")
                continue
        except (ContactStorageError, TypeError, ValueError) as error:
            print(f"Error: {error}")
        else:
            if choice == "1":
                print("Contact added and saved.")
