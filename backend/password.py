"""
password.py

This module provides the PasswordHash class: a wrapper around a string that bundles along with it
the relevant logic.

NOTE: Logic relevant to authentication should use this class instead of a regular `str` to represent
the password hash, to ensure at a type system level that no un-hashed password is stored.

Some relevant reading: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
"""

from typing import override


class PasswordHash:
    def __init__(self, value: str) -> None:
        # TODO: Put `value` through the argon2id hashing algorithm
        self.value = value

    @override
    def __eq__(self, other) -> bool:
        return self.value == other.value

    @override
    def __str__(self) -> str:
        return self.value
