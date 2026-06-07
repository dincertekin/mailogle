#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class Hudsonrock(BaseModule):
    name = "HudsonRock"

    def check(self, email):
        session = self.create_session()

        url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={email}"

        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'application/json',
        }

        response = self.request_with_retry(session, "GET", url, headers=headers)
        data = response.json()

        breached = not (
            data.get("stealers") == []
            and data.get("total_corporate_services") == 0
            and data.get("total_user_services") == 0
        )

        return self.report(breached)
