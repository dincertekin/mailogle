from modules.instagram import Instagram

LOGIN_URL = "https://www.instagram.com/accounts/login/"
SIGNUP_URL = "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/"
LOGIN_HTML = '<html><script>window.__additionalData = {"csrf_token":"abc123"};</script></html>'


def test_returns_found_when_email_is_taken(requests_mock):
    requests_mock.get(LOGIN_URL, text=LOGIN_HTML)
    requests_mock.post(SIGNUP_URL, json={"errors": {"email": [{"code": "email_is_taken"}]}})

    assert Instagram().run_scan("test@example.com").found is True


def test_returns_found_with_a_note_when_sharing_limit_is_reached(requests_mock):
    requests_mock.get(LOGIN_URL, text=LOGIN_HTML)
    requests_mock.post(SIGNUP_URL, json={"errors": {"email": [{"code": "email_sharing_limit"}]}})

    result = Instagram().run_scan("test@example.com")
    assert result.found is True
    assert result.detail == "sharing limit reached"


def test_returns_not_found_when_email_is_available(requests_mock):
    requests_mock.get(LOGIN_URL, text=LOGIN_HTML)
    requests_mock.post(SIGNUP_URL, json={})

    assert Instagram().run_scan("test@example.com").found is False


def test_returns_a_clear_error_when_rate_limited(requests_mock):
    requests_mock.get(LOGIN_URL, text=LOGIN_HTML)
    requests_mock.post(SIGNUP_URL, status_code=429)

    result = Instagram().run_scan("test@example.com")
    assert result.found is None
    assert result.detail == "Instagram is rate-limiting/blocking signup checks from this IP. Try again later."


def test_returns_an_error_when_csrf_token_is_missing(requests_mock):
    requests_mock.get(LOGIN_URL, text="<html></html>")

    result = Instagram().run_scan("test@example.com")
    assert result.found is None
    assert result.detail == "CSRF token not found in login page!"
