import re

from modules.spotify import Spotify

URL = re.compile(r"https://spclient\.wg\.spotify\.com/signup/public/v1/account")


def test_returns_found_when_email_is_registered(requests_mock):
    requests_mock.get(URL, json={"status": 20})

    assert Spotify().run_scan("test@example.com").found is True


def test_returns_not_found_when_email_is_not_registered(requests_mock):
    requests_mock.get(URL, json={"status": 1})

    assert Spotify().run_scan("test@example.com").found is False


def test_returns_an_error_on_http_failure(requests_mock):
    requests_mock.get(URL, status_code=500)

    result = Spotify().run_scan("test@example.com")
    assert result.found is None
    assert result.detail
