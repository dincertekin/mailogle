#!/usr/bin/env python3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import random
import requests
import time

# Shared pool of desktop User-Agents. Modules that need a specific
# UA (e.g. a mobile API endpoint) can override it locally.
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]

# Populated by the @register decorator; mailogle.py reads this after
# importing every file in modules/ so it never has to guess class names.
MODULES = {}


def register(cls):
    MODULES[cls.__name__.lower()] = cls
    return cls


@dataclass
class ScanResult:
    """Outcome of a single module's scan, rendered as one row in the results table.

    `found` is a tri-state: True (account exists), False (it doesn't),
    or None (the check couldn't be completed - see `detail` for why).
    """

    name: str
    found: Optional[bool]
    detail: Optional[str] = None


class BaseModule(ABC):
    """Common scaffolding for a platform check.

    Subclasses only need to set `name` and implement `check(email)`,
    returning the result of self.report(...)/self.error(...).
    See modules/_template.py for a copy-paste starting point.
    """

    name = None

    def __init__(self):
        if self.name is None:
            self.name = type(self).__name__
        self.detail = None

    @staticmethod
    def random_user_agent():
        return random.choice(USER_AGENTS)

    @staticmethod
    def create_session():
        return requests.Session()

    def report(self, found, extra=None):
        """Record that the check completed; `found` is True/False, `extra` an optional note."""
        self.detail = extra
        return found

    def error(self, message):
        """Record that the check could not be completed and why."""
        self.detail = message
        return None

    def request_with_retry(self, session, method, url, max_retries=3, backoff=1.0, **kwargs):
        """Issue a request, retrying with backoff when rate-limited (HTTP 429)."""
        response = session.request(method, url, **kwargs)
        for attempt in range(max_retries - 1):
            if response.status_code != 429:
                break
            time.sleep(backoff * (attempt + 1))
            response = session.request(method, url, **kwargs)
        return response

    def run_scan(self, email):
        self.detail = None
        try:
            found = self.check(email)
        except Exception as e:
            found = self.error(str(e))
        return ScanResult(name=self.name, found=found, detail=self.detail)

    @abstractmethod
    def check(self, email):
        """Return True/False/None (via self.report/self.error) for "account exists"."""
