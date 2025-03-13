from backend.password import PasswordHash
from hypothesis import given, assume, strategies as st

@given(st.text())
def test_passwordhash_equality_same_value(value: str):
    """
    Test that two PasswordHash instances with the same value compare equal.
    """
    hashOne = PasswordHash(value)
    hashTwo = PasswordHash(value)
    assert hashOne == hashTwo

@given(st.tuples(st.text(), st.text()))
def test_passwordhash_inequality_different_value(values):
    """
    Test that two PasswordHash instances with different values compare not equal.
    """
    passwordOne, passwordTwo = values
    # Ensure we only test when the two values are indeed different.
    assume(passwordOne != passwordTwo)
    hashOne = PasswordHash(passwordOne)
    hashTwo = PasswordHash(passwordTwo)
    assert hashOne != hashTwo

@given(st.text())
def test_passwordhash_comparison_different_type(value: str):
    """Test that comparing a PasswordHash instance to a plain string returns False."""
    hash = PasswordHash(value)
    assert hash != value
