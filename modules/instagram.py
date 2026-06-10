#!/usr/bin/env python3
import re
from modules.base import BaseModule, register


@register
class Instagram(BaseModule):
    name = "Instagram"

    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.6 Mobile/15E148 Safari/604.1"
    )

    def check(self, email):
        session = self.create_session()

        base_headers = {
            "User-Agent": self.MOBILE_UA,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "DNT": "1",
            "Connection": "keep-alive",
        }

        csrf_token = self.get_csrf_token(session, base_headers)
        if not csrf_token:
            return None

        base_headers.update({
            "x-csrftoken": csrf_token,
            "x-ig-app-id": "936619743392459",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded",
        })

        url = "https://www.instagram.com/api/v1/users/check_email/"
        data = {"email": email, "sign_up_code": ""}

        response = self.request_with_retry(
            session, "POST", url, headers=base_headers, data=data, timeout=10
        )

        if response.status_code == 200:
            body = response.json()
            if body.get("error_type") == "email_is_taken":
                return self.report(True)
            elif body.get("available") is True:
                return self.report(False)
            return self.error(f"Unexpected 200 body: {body}")

        elif response.status_code == 400:
            body = response.json()
            if body.get("spam") is True:
                return self.report(False)
            return self.error(f"Unexpected 400 body: {body}")

        elif response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        return self.error(f"Request failed with status {response.status_code}.")

    def get_csrf_token(self, session, headers):
        try:
            response = session.get(
                "https://www.instagram.com/", headers=headers, timeout=10
            )
        except Exception as e:
            self.error(f"Failed to fetch homepage: {e}")
            return None

        if response.status_code != 200:
            self.error(f"Homepage returned {response.status_code}.")
            return None

        csrf = session.cookies.get("csrftoken")
        if not csrf:
            match = re.search(
                r'["\']csrf_token["\']\s*:\s*["\']([^"\']+)["\']', response.text
            )
            if match:
                csrf = match.group(1)

        if not csrf:
            self.error("CSRF token not found. IP may be flagged.")
            return None

        return csrf
