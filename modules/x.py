#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class X(BaseModule):
    name = "X"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "x-twitter-client-language": "en",
        "sec-ch-ua-mobile": "?1",
        "x-twitter-active-user": "yes",
        "origin": "https://x.com",
    }

    def check(self, email):
        session = self.create_session()

        response = self.request_with_retry(
            session, "GET",
            "https://api.x.com/i/users/email_available.json",
            headers=self.HEADERS,
            params={"email": email},
            timeout=10,
        )

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        data = response.json()
        taken = data.get("taken")

        if taken is True:
            return self.report(True)
        elif taken is False:
            return self.report(False)
        else:
            return self.error(f"Unexpected response body: {data}")
