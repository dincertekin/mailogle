#!/usr/bin/env python3
import hashlib

from modules.base import BaseModule, register


@register
class Gravatar(BaseModule):
    name = "Gravatar"

    def check(self, email):
        session = self.create_session()

        # Gravatar's API mandates an MD5 hash of the trimmed, lower-cased
        # email as the lookup key - this isn't a security use of MD5.
        email_hash = hashlib.md5(email.strip().lower().encode(), usedforsecurity=False).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"

        headers = {'User-Agent': self.random_user_agent()}

        response = self.request_with_retry(session, "GET", url, headers=headers, timeout=10)

        if response.status_code == 200:
            return self.report(True)
        elif response.status_code == 404:
            return self.report(False)
        else:
            return self.error(f"Request failed with status code {response.status_code}.")
