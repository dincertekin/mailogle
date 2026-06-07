import hashlib
import re

from modules.gravatar import Gravatar

URL = re.compile(r"https://www\.gravatar\.com/avatar/")


def test_returns_found_when_avatar_exists(requests_mock):
    requests_mock.get(URL, status_code=200)

    assert Gravatar().run_scan("test@example.com").found is True


def test_returns_not_found_when_avatar_is_missing(requests_mock):
    requests_mock.get(URL, status_code=404)

    assert Gravatar().run_scan("test@example.com").found is False


def test_returns_an_error_on_unexpected_status(requests_mock):
    requests_mock.get(URL, status_code=500)

    result = Gravatar().run_scan("test@example.com")
    assert result.found is None


def test_looks_up_the_md5_hash_of_the_normalised_email(requests_mock):
    requests_mock.get(URL, status_code=404)

    Gravatar().run_scan("  Test@Example.com  ")

    expected_hash = hashlib.md5(b"test@example.com", usedforsecurity=False).hexdigest()
    assert expected_hash in requests_mock.last_request.url
