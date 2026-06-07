#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class Snapchat(BaseModule):
    name = "Snapchat"

    def check(self, email):
        session = self.create_session()

        headers = {'User-Agent': self.random_user_agent()}
        data = {'email': email}

        response = self.request_with_retry(
            session, "POST", "https://bitmoji.api.snapchat.com/api/user/find", headers=headers, json=data, timeout=10
        )
        response.raise_for_status()

        exists = '{"account_type":"snapchat"}' in response.text
        return self.report(exists)
