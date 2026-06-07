#!/usr/bin/env python3
import re

from modules.base import BaseModule, register


@register
class Github(BaseModule):
    name = "GitHub"

    def check(self, email):
        session = self.create_session()

        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://github.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        csrf_token = self.get_csrf_token(session, headers)
        if not csrf_token:
            return None  # error already recorded by get_csrf_token

        data = {
            "value": email,
            "authenticity_token": csrf_token,
        }

        response = self.request_with_retry(
            session, "POST", "https://github.com/signup_check/email", headers=headers, data=data
        )

        if response.status_code == 422:
            # GitHub returns 422 both for "email taken" (JSON) and for its generic
            # anti-automation challenge page (HTML, titled "Oh no") - only the
            # former is a real signal, the latter would otherwise read as a false positive.
            if 'application/json' in response.headers.get('Content-Type', ''):
                return self.report(True)
            return self.error("GitHub blocked the request (anti-automation challenge).")
        elif response.status_code == 200:
            return self.report(False)
        elif response.status_code == 429:
            return self.error("Too many requests.")
        else:
            return self.error(f"Request failed with status code {response.status_code}.")

    def get_csrf_token(self, session, headers):
        response = session.get("https://github.com/join", headers=headers)
        if response.status_code != 200:
            self.error("Failed to retrieve join(sign up) page!")
            return None

        match = re.search(r'<input[^>]+name="authenticity_token"[^>]+value="([^"]+)"', response.text)
        if not match:
            self.error("CSRF token not found!")
            return None

        return match.group(1)
