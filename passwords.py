"""Password-strength validation for the Day 5 exercises."""

import string


class WeakPasswordError(ValueError):
    """Raised when a password does not meet the strength requirements."""


def strong_password(password: str) -> bool:
    """Return True for a strong password; raise WeakPasswordError otherwise."""
    if not isinstance(password, str):
        raise TypeError("password must be a string")

    requirements = (
        (len(password) >= 8, "at least 8 characters"),
        (any(character.isupper() for character in password), "an uppercase letter"),
        (any(character.isdigit() for character in password), "a number"),
        (
            any(character in string.punctuation for character in password),
            "a special character",
        ),
    )
    missing_requirements = [
        description for passed, description in requirements if not passed
    ]

    if missing_requirements:
        missing_text = ", ".join(missing_requirements)
        raise WeakPasswordError(f"password must contain {missing_text}")

    return True
