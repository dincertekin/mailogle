#!/usr/bin/env python3
import json
import time

from modules.base import BaseModule, register


@register
class Pinterest(BaseModule):
    name = "Pinterest"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "x-pinterest-pws-handler": "www/signup/[step].js",
        "x-app-version": "2503cde",
        "x-requested-with": "XMLHttpRequest",
        "x-pinterest-source-url": "/signup/step1/",
        "x-pinterest-appstate": "active",
        "origin": "https://www.pinterest.com",
        "referer": "https://www.pinterest.com/",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

    def check(self, email):
        session = self.create_session()

        params = {
            "source_url": "/signup/step1/",
            "data": json.dumps(
                {
                    "options": {
                        "url": "/v3/register/exists/",
                        "data": {"email": email},
                    },
                    "context": {},
                },
                separators=(",", ":"),
            ),
            "_": str(int(time.time() * 1000)),
        }

        response = self.request_with_retry(
            session, "GET",
            "https://www.pinterest.com/resource/ApiResource/get/",
            headers=self.HEADERS,
            params=params,
            timeout=10,
        )

        if response.status_code == 403:
            return self.error("Blocked by WAF or IP ban (403).")

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        data = response.json()
        exists = data.get("resource_response", {}).get("data")

        if exists is True:
            return self.report(True)
        elif exists is False:
            return self.report(False)

        return self.error(f"Unexpected response body: {data}")
