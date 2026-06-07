#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class Spotify(BaseModule):
    name = "Spotify"

    # Spotify's signup endpoint is mobile-only; the shared desktop UA pool gets rejected.
    USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"

    def check(self, email):
        session = self.create_session()

        url = f"https://spclient.wg.spotify.com/signup/public/v1/account?validate=1&email={email}"
        headers = {'User-Agent': self.USER_AGENT}

        response = self.request_with_retry(session, "GET", url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        return self.report(data.get("status") == 20)
