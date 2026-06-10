#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class MyFitnessPal(BaseModule):
    name = "MyFitnessPal"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "identity",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "Referer": "https://www.myfitnesspal.com/account/create",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def check(self, email):
        session = self.create_session()

        response = self.request_with_retry(
            session, "GET",
            "https://www.myfitnesspal.com/api/idm/user-exists",
            headers=self.HEADERS,
            params={"email": email},
            timeout=10,
        )

        if response.status_code == 403:
            return self.error("Blocked by WAF or IP ban (403).")

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        data = response.json()
        exists = data.get("emailExists")

        if exists is True:
            return self.report(True)
        elif exists is False:
            return self.report(False)

        return self.error(f"Unexpected response body: {data}")
