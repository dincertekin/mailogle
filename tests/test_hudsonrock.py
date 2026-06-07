import re

from modules.hudsonrock import Hudsonrock

URL = re.compile(r"https://cavalier\.hudsonrock\.com/api/json/v2/osint-tools/search-by-email")


def test_returns_found_when_breaches_are_found(requests_mock):
    requests_mock.get(URL, json={"stealers": ["redline"], "total_corporate_services": 1, "total_user_services": 2})

    assert Hudsonrock().run_scan("test@example.com").found is True


def test_returns_not_found_when_no_breaches_are_found(requests_mock):
    requests_mock.get(URL, json={"stealers": [], "total_corporate_services": 0, "total_user_services": 0})

    assert Hudsonrock().run_scan("test@example.com").found is False
