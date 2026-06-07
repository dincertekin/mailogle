#!/usr/bin/env python3
from bs4 import BeautifulSoup
import random
import string

from modules.base import BaseModule, register


@register
class Instagram(BaseModule):
    name = "Instagram"

    def check(self, email):
        session = self.create_session()

        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.instagram.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        csrf_token = self.get_csrf_token(session, headers)
        if not csrf_token:
            return None  # error already recorded by get_csrf_token
        headers["x-csrftoken"] = csrf_token

        data = {
            'email': email,
            'username': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),
            'first_name': '',
            'opt_into_one_tap': 'false',
        }

        url = "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/"
        response = self.request_with_retry(session, "POST", url, headers=headers, data=data, timeout=10)

        if response.status_code == 429:
            return self.error("Instagram is rate-limiting/blocking signup checks from this IP. Try again later.")
        elif response.status_code != 200:
            return self.error(f"Request failed with status code {response.status_code}.")

        body = response.json()
        email_errors = body.get('errors', {}).get('email')

        if email_errors and email_errors[0].get('code') == 'email_is_taken':
            return self.report(True)
        elif 'email_sharing_limit' in str(body.get('errors', {})):
            return self.report(True, extra="sharing limit reached")
        else:
            return self.report(False)

    def get_csrf_token(self, session, headers):
        response = session.get("https://www.instagram.com/accounts/login/", headers=headers)

        if response.status_code != 200:
            return self.error("Failed to retrieve login page!")

        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup.find_all('script'):
            if 'csrf_token' in script.text:
                return script.text.split('csrf_token":"')[1].split('"')[0]

        return self.error("CSRF token not found in login page!")
