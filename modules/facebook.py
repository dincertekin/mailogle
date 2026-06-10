#!/usr/bin/env python3
import re

from modules.base import BaseModule, register


@register
class Facebook(BaseModule):
    name = "Facebook"

    def check(self, email):
        session = self.create_session()

        try:
            session.get(
                "https://m.facebook.com/login/",
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "identity",
                    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                },
                timeout=10,
                allow_redirects=False,
            )
        except Exception as e:
            return self.error(f"Failed to seed cookies: {e}")

        try:
            res = session.get(
                "https://www.facebook.com",
                params={"_rdr": ""},
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "identity",
                    "upgrade-insecure-requests": "1",
                    "sec-fetch-site": "cross-site",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-user": "?1",
                    "sec-fetch-dest": "document",
                    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Linux"',
                    "referer": "https://www.google.com/",
                    "accept-language": "en-US,en;q=0.9",
                },
                timeout=10,
                allow_redirects=False,
            )
        except Exception as e:
            return self.error(f"Failed to fetch Facebook homepage: {e}")

        html = res.text

        lsd_match = (
            re.search(r'\["LSD",\[\],\{"token":"([^"]+)"\}', html)
            or re.search(r'name="lsd"\s+value="([^"]+)"', html)
            or re.search(r'"lsd":"([^"]+)"', html)
        )
        j_match = (
            re.search(r'jazoest=(\d+)', html)
            or re.search(r'name="jazoest"\s+value="(\d+)"', html)
        )

        lsd = lsd_match.group(1) if lsd_match else None
        jazoest = j_match.group(1) if j_match else None

        if not lsd or not jazoest:
            return self.error(f"Token extraction failed (LSD: {bool(lsd)}, jazoest: {bool(jazoest)})")

        data = {
            "jazoest": jazoest,
            "lsd": lsd,
            "email": email,
            "did_submit": "1",
            "__user": "0",
            "__a": "1",
            "__req": "7",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept-Encoding": "identity",
            "sec-ch-ua-full-version-list": '"Google Chrome";v="143.0.7499.192", "Chromium";v="143.0.7499.192", "Not A(Brand";v="24.0.0.0"',
            "sec-ch-ua-platform": '"Linux"',
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-model": '""',
            "sec-ch-ua-mobile": "?0",
            "x-asbd-id": "359341",
            "x-fb-lsd": lsd,
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua-platform-version": '""',
            "origin": "https://www.facebook.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0",
            "accept-language": "en-US,en;q=0.9",
        }

        response = self.request_with_retry(
            session, "POST",
            "https://www.facebook.com/ajax/login/help/identify.php",
            params={"ctx": "recover"},
            headers=headers,
            data=data,
            timeout=10,
        )

        body = response.text

        if "These accounts matched your search" in body or "redirectPageTo" in body:
            return self.report(True)
        elif "No search results" in body or "Your search did not return any results." in body:
            return self.report(False)
        else:
            return self.error(f"Unexpected response (HTTP {response.status_code}).")
