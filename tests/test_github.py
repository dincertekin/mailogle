from modules.github import Github

JOIN_URL = "https://github.com/join"
SIGNUP_CHECK_URL = "https://github.com/signup_check/email"
JOIN_HTML = '<html><input type="hidden" name="authenticity_token" value="test-token"></html>'


def test_returns_found_when_email_is_taken(requests_mock):
    requests_mock.get(JOIN_URL, text=JOIN_HTML)
    requests_mock.post(
        SIGNUP_CHECK_URL,
        status_code=422,
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={"value": "test@example.com", "valid": False},
    )

    assert Github().run_scan("test@example.com").found is True


def test_returns_an_error_when_blocked_by_the_anti_automation_challenge(requests_mock):
    requests_mock.get(JOIN_URL, text=JOIN_HTML)
    requests_mock.post(
        SIGNUP_CHECK_URL,
        status_code=422,
        headers={"Content-Type": "text/html; charset=utf-8"},
        text="<html><head><title>Oh no &middot; GitHub</title></head></html>",
    )

    result = Github().run_scan("test@example.com")
    assert result.found is None
    assert result.detail == "GitHub blocked the request (anti-automation challenge)."


def test_returns_not_found_when_email_is_available(requests_mock):
    requests_mock.get(JOIN_URL, text=JOIN_HTML)
    requests_mock.post(SIGNUP_CHECK_URL, status_code=200)

    assert Github().run_scan("test@example.com").found is False


def test_returns_an_error_when_csrf_token_is_missing(requests_mock):
    requests_mock.get(JOIN_URL, text="<html></html>")

    result = Github().run_scan("test@example.com")
    assert result.found is None
    assert result.detail == "CSRF token not found!"


def test_returns_an_error_when_join_page_is_unreachable(requests_mock):
    requests_mock.get(JOIN_URL, status_code=503)

    result = Github().run_scan("test@example.com")
    assert result.found is None
    assert result.detail == "Failed to retrieve join(sign up) page!"
