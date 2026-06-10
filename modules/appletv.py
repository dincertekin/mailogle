#!/usr/bin/env python3
import json

from modules.base import BaseModule, register


@register
class AppleTV(BaseModule):
    name = "Apple TV"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "X-Apple-Domain-Id": "2",
        "X-Apple-Locale": "en_us",
        "X-Apple-Auth-Context": "tv",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://idmsa.apple.com",
        "Referer": "https://idmsa.apple.com/",
    }

    def check(self, email):
        session = self.create_session()

        response = self.request_with_retry(
            session, "POST",
            "https://idmsa.apple.com/appleauth/auth/federate",
            headers=self.HEADERS,
            params={"isRememberMeEnabled": "false"},
            data=json.dumps({"accountName": email, "rememberMe": False}),
            timeout=10,
        )

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        data = response.json()

        if "primaryAuthOptions" in data:
            return self.report(True)

        return self.report(False)
