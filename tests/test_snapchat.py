from modules.snapchat import Snapchat

URL = "https://bitmoji.api.snapchat.com/api/user/find"


def test_returns_found_when_account_exists(requests_mock):
    requests_mock.post(URL, text='{"account_type":"snapchat"}')

    assert Snapchat().run_scan("test@example.com").found is True


def test_returns_not_found_when_account_does_not_exist(requests_mock):
    requests_mock.post(URL, text='{"account_type":"unknown"}')

    assert Snapchat().run_scan("test@example.com").found is False


def test_returns_an_error_on_http_failure(requests_mock):
    requests_mock.post(URL, status_code=500)

    result = Snapchat().run_scan("test@example.com")
    assert result.found is None
    assert result.detail
