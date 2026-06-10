#!/usr/bin/env python3
import re

from modules.base import BaseModule, register


@register
class Github(BaseModule):
    name = "GitHub"

    SIGNUP_HEADERS = {
        "host": "github.com",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.google.com/",
        "accept-language": "en-US,en;q=0.9",
    }

    CHECK_HEADERS = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "origin": "https://github.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://github.com/signup",
        "accept-language": "en-US,en;q=0.9",
    }

    def check(self, email):
        session = self.create_session()

        csrf_token = self.get_csrf_token(session)
        if not csrf_token:
            return None

        data = {
            "authenticity_token": csrf_token,
            "value": email,
        }

        response = self.request_with_retry(
            session, "POST", "https://github.com/email_validity_checks",
            headers=self.CHECK_HEADERS, data=data, timeout=10
        )

        body = response.text

        if "already associated with an account" in body:
            return self.report(True)
        elif response.status_code == 200 and "Email is available" in body:
            return self.report(False)
        elif response.status_code == 429:
            return self.error("Too many requests.")
        else:
            return self.error(f"Unexpected response (HTTP {response.status_code}).")

    def get_csrf_token(self, session):
        try:
            response = session.get(
                "https://github.com/signup", headers=self.SIGNUP_HEADERS, timeout=10
            )
        except Exception as e:
            self.error(f"Failed to fetch signup page: {e}")
            return None

        if response.status_code != 200:
            self.error(f"Signup page returned {response.status_code}.")
            return None

        match = re.search(r'data-csrf="true"\s+value="([^"]+)"', response.text)
        if not match:
            self.error("CSRF token not found.")
            return None

        return match.group(1)
