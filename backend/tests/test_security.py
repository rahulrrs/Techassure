from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    hashed = hash_password("ChangeMe123!")
    assert hashed != "ChangeMe123!"
    assert verify_password("ChangeMe123!", hashed)


def test_access_token_created():
    token = create_access_token("admin@techassure.local", {"role": "Admin"})
    assert token.count(".") == 2
