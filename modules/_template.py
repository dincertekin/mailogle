#!/usr/bin/env python3
# Copy this file to modules/<platform>.py (drop the leading underscore -
# the loader skips files that start with one) and fill in the TODOs.
#
# `name` is what gets shown in the scan output, `check` does the actual
# work and must end by calling self.report(...). BaseModule already
# gives you: self.create_session(), self.random_user_agent(),
# self.request_with_retry(...), self.report(...) and self.error(...).
# Unhandled exceptions are caught and reported automatically.

from modules.base import BaseModule, register


@register
class Template(BaseModule):
    name = "Template"  # TODO: replace with the platform's display name

    def check(self, email):
        session = self.create_session()

        # TODO: replace with the real signup/lookup endpoint
        url = "https://example.com/api/check-email"

        headers = {
            "User-Agent": self.random_user_agent(),
        }

        response = self.request_with_retry(session, "POST", url, headers=headers, json={"email": email}, timeout=10)

        if response.status_code != 200:
            return self.error(f"Request failed with status code {response.status_code}.")

        # TODO: replace with the real condition that means "account exists"
        exists = response.json().get("exists", False)

        return self.report(exists)
