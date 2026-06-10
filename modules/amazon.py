#!/usr/bin/env python3
import re
from html import unescape

from modules.base import BaseModule, register


@register
class Amazon(BaseModule):
    name = "Amazon"

    SIGNIN_URL = (
        "https://www.amazon.com/ap/signin?"
        "openid.pape.max_auth_age=0"
        "&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F"
        "%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin"
        "&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select"
        "&openid.assoc_handle=usflex"
        "&openid.mode=checkid_setup"
        "&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select"
        "&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
    )

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def check(self, email):
        session = self.create_session()
        session.headers.update(self.HEADERS)

        try:
            resp = session.get(self.SIGNIN_URL, timeout=10, allow_redirects=True)
        except Exception as e:
            return self.error(f"Failed to load sign-in page: {e}")

        if resp.status_code != 200:
            return self.error(f"Sign-in page returned {resp.status_code}.")

        if self._is_captcha(resp.text):
            return self.error("CAPTCHA detected. IP may be flagged.")

        data = self._extract_form_fields(resp.text)
        if not data:
            return self.error("Could not extract form fields.")

        data["email"] = email

        post_url = self._extract_form_action(resp.text)
        if not post_url:
            return self.error("Could not find sign-in form action URL.")
        if post_url.startswith("/"):
            post_url = "https://www.amazon.com" + post_url

        response = self.request_with_retry(
            session, "POST", post_url, data=data, timeout=10, allow_redirects=True
        )

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code not in (200, 302):
            return self.error(f"Unexpected response (HTTP {response.status_code}).")

        if self._is_captcha(response.text):
            return self.report(True)

        if 'id="auth-password-missing-alert"' in response.text:
            return self.report(True)

        return self.report(False)

    @staticmethod
    def _extract_form_fields(html: str) -> dict:
        """Pull hidden inputs from only the signIn form, like the Go version."""

        form_match = re.search(
            r'(?s)<form[^>]*name=["\']signIn["\'][^>]*>(.*?)</form>',
            html, re.IGNORECASE
        )
        if not form_match:
            return {}

        fields = {}
        for tag in re.finditer(
            r'<input[^>]+type=["\']hidden["\'][^>]+>', form_match.group(1), re.IGNORECASE
        ):
            tag_str = tag.group(0)
            name = re.search(r'name=["\']([^"\']*)["\']', tag_str)
            value = re.search(r'value=["\']([^"\']*)["\']', tag_str)
            if name and value:
                fields[name.group(1)] = value.group(1)
        return fields

    @staticmethod
    def _is_captcha(html: str) -> bool:
        lower = html.lower()
        return any(
            marker in lower
            for marker in ("captcha", "type the characters", "robot check", "opf-captcha")
        )

    @staticmethod
    def _extract_form_action(html: str) -> str | None:
        """Find the signIn or claim form action URL regardless of attribute order."""
        for form_tag in re.finditer(r"<form\s[^>]*>", html, re.IGNORECASE):
            tag = form_tag.group(0)
            action_match = re.search(r'action=["\']([^"\']*)["\']', tag)
            if not action_match:
                continue
            action = unescape(action_match.group(1))
            name_match = re.search(r'name=["\']([^"\']*)["\']', tag)
            if name_match and name_match.group(1) == "signIn":
                return action
            if "/ap/signin" in action or "/ax/claim" in action:
                return action
        return None
