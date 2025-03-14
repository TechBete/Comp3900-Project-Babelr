from backend.password import PasswordHash
from pytest import raises
from hypothesis import given, assume, strategies as st

@given(st.text( min_size = 1 ))
def test_passwordhash_equality_different_value(value: str):
    """
    Test that two PasswordHash instances with the same value are not equal (due to salting).
    """
    hashOne = PasswordHash(value)
    hashTwo = PasswordHash(value)
    assert hashOne != hashTwo

@given(st.text( min_size = 1 ))
def test_passwordhash_verify_same_password(password: str):
    """
    Test that the `PasswordHash verifies the original password.`
    """
    hash = PasswordHash(password)
    assert hash == password 

@given(st.text( min_size = 1 ), st.text( min_size = 1 ))
def test_passwordhash_deny_different_password(password: str, notPassword: str):
    """
    Test that the `PasswordHash verifies the original password.`
    """
    assume(password != notPassword)
    hash = PasswordHash(password)
    assert (hash != notPassword)

@given(st.tuples(st.text(min_size = 1), st.text(min_size = 1)))
def test_passwordhash_inequality_different_value(passwords):
    """
    Test that two PasswordHash instances with different values compare not equal.
    """
    passwordOne, passwordTwo = passwords
    # Ensure we only test when the two values are indeed different.
    assume(passwordOne != passwordTwo)
    hashOne = PasswordHash(passwordOne)
    hashTwo = PasswordHash(passwordTwo)
    assert hashOne != hashTwo

@given(st.text(min_size = 1), st.one_of(st.integers(), st.floats(), st.booleans(), st.lists(st.integers())))
def test_passwordhash_comparison_different_type(password: str, notPassword):
    """
    Test that comparing a PasswordHash instance to any other type returns False.
    """
    hash = PasswordHash(password)
    assert hash != notPassword

@given(st.text())
def test_passwordhash_cannot_be_empty(password: str):
    """
    Test that empty values are not accepted by PasswordHash.
    """
    if (len(password) == 0):
        with raises(ValueError, match="Password cannot be empty"):
            PasswordHash("")
