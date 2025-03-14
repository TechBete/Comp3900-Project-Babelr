"""
password.py

This module provides the PasswordHash class: a wrapper around a string that bundles along with it
the relevant logic.

NOTE: Logic relevant to authentication should use this class instead of a regular `str` to represent
the password hash, to ensure at a type system level that no un-hashed password is stored.

Some relevant reading: https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
"""

from typing import override
from passlib.hash import argon2
import os

ALGO = argon2.using(
    type=os.getenv("ARGON2_TYPE", "ID"),
    rounds=int(os.getenv("ARGON2_ROUNDS", 8)),
)

class PasswordHash:
    value: str

    def __init__(self, value: str) -> None:
        """
        Given a password, initialise an instance of PasswordHash by hashing it and storing it in
        `value`.
        """
        if not value:
            raise ValueError("Password cannot be empty")
        self.value = ALGO.hash(value)

    def verify(self, password: str) -> bool:
        """
        Verify that the given `password` is equivalent to that which was used to initialise this
        instance of `PasswordHash`.
        """
        return ALGO.verify(password, self.value)

    @staticmethod
    def hash_password(password: str) -> str:
        if not password:
            raise ValueError("Password cannot be empty")
        return ALGO.hash(password)

    @override
    def __eq__(self, other) -> bool:
        """
        Check if two instances of PasswordHash are equal.
        """
        if isinstance(other, PasswordHash):
            return self.value == other.value
        if isinstance (other, str):
            return self.verify(other)
        return NotImplemented


    @override
    def __str__(self) -> str:
        """
        Get the inner value.
        """
        return self.value
