#!/usr/bin/env python3
from modules.base import BaseModule, register


@register
class Wordpress(BaseModule):
    name = "WordPress"

    def check(self, email):
        session = self.create_session()

        url = "https://public-api.wordpress.com/rest/v1.1/signups/validation/user/"
        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'application/json',
        }
        data = {'email': email, 'locale': 'en'}

        response = self.request_with_retry(session, "POST", url, headers=headers, data=data, timeout=10)

        if response.status_code != 200:
            return self.error(f"Request failed with status code {response.status_code}.")

        taken = 'taken' in response.json().get('messages', {}).get('email', {})
        return self.report(taken)
