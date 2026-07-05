from app.api.routes import auth


def test_login_throttle_blocks_after_repeated_failures() -> None:
    email = "owner@example.com"
    auth._failed_logins.clear()

    for _ in range(auth.MAX_FAILED_LOGINS):
        auth._record_failed_login(email)

    assert auth._is_login_limited(email)


def test_login_throttle_clears_successful_email() -> None:
    email = "owner@example.com"
    auth._failed_logins.clear()
    auth._record_failed_login(email)

    auth._failed_logins.pop(email, None)

    assert not auth._is_login_limited(email)
