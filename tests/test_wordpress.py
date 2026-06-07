from modules.wordpress import Wordpress

URL = "https://public-api.wordpress.com/rest/v1.1/signups/validation/user/"


def test_returns_found_when_email_is_taken(requests_mock):
    requests_mock.post(
        URL,
        json={"success": False, "messages": {"email": {"taken": "An account with this email already exists."}}},
    )

    assert Wordpress().run_scan("test@example.com").found is True


def test_returns_not_found_when_email_is_available(requests_mock):
    requests_mock.post(
        URL,
        json={"success": False, "messages": {"email": {"invalid": "Use a different email address."}}},
    )

    assert Wordpress().run_scan("test@example.com").found is False


def test_returns_an_error_on_http_failure(requests_mock):
    requests_mock.post(URL, status_code=500)

    result = Wordpress().run_scan("test@example.com")
    assert result.found is None
