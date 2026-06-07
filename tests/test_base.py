from modules.base import BaseModule, MODULES, ScanResult, register


class DummyModule(BaseModule):
    name = "Dummy"

    def check(self, email):
        return True


def test_report_returns_the_found_flag_and_records_the_note():
    module = DummyModule()
    assert module.report(True, extra="sharing limit reached") is True
    assert module.detail == "sharing limit reached"
    assert module.report(False) is False
    assert module.detail is None


def test_error_returns_none_and_records_the_message():
    module = DummyModule()
    assert module.error("boom") is None
    assert module.detail == "boom"


def test_register_adds_class_to_module_registry():
    @register
    class Probe(BaseModule):
        def check(self, email):
            return True

    try:
        assert MODULES["probe"] is Probe
    finally:
        del MODULES["probe"]


def test_request_with_retry_retries_on_429_then_succeeds(requests_mock):
    url = "https://example.com/check"
    requests_mock.get(
        url,
        [
            {"status_code": 429},
            {"status_code": 429},
            {"status_code": 200, "text": "ok"},
        ],
    )

    module = DummyModule()
    session = module.create_session()
    response = module.request_with_retry(session, "GET", url, max_retries=3, backoff=0)

    assert response.status_code == 200
    assert requests_mock.call_count == 3


def test_request_with_retry_gives_up_after_max_retries(requests_mock):
    url = "https://example.com/check"
    requests_mock.get(url, status_code=429)

    module = DummyModule()
    session = module.create_session()
    response = module.request_with_retry(session, "GET", url, max_retries=2, backoff=0)

    assert response.status_code == 429
    assert requests_mock.call_count == 2


def test_run_scan_returns_a_scan_result_for_a_match():
    result = DummyModule().run_scan("test@example.com")

    assert result == ScanResult(name="Dummy", found=True, detail=None)


def test_run_scan_catches_exceptions_and_records_them_as_errors():
    class BoomModule(BaseModule):
        name = "Boom"

        def check(self, email):
            raise RuntimeError("network exploded")

    result = BoomModule().run_scan("test@example.com")

    assert result == ScanResult(name="Boom", found=None, detail="network exploded")
