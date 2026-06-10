#!/usr/bin/env python3
import json

from modules.base import BaseModule, register


@register
class Spotify(BaseModule):
    name = "Spotify"

    SEED_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "identity",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "upgrade-insecure-requests": "1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.spotify.com/us/signup",
        "accept-language": "en-US,en;q=0.9",
    }

    POST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept-Encoding": "identity",
        "Content-Type": "application/json",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "origin": "https://www.spotify.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.spotify.com/",
        "accept-language": "en-US,en;q=0.9",
    }

    def check(self, email):
        session = self.create_session()

        # Seed cookies via the signup page
        try:
            session.get(
                "https://www.spotify.com/in-en/signup",
                headers=self.SEED_HEADERS,
                timeout=10,
            )
        except Exception as e:
            return self.error(f"Failed to seed cookies: {e}")

        payload = json.dumps({
            "fields": [
                {
                    "field": "FIELD_EMAIL",
                    "value": email,
                }
            ],
            "client_info": {
                "api_key": "a1e486e2729f46d6bb368d6b2bcda326",
                "app_version": "v2",
                "capabilities": [1],
                "installation_id": "3740cfb5-c76f-4ae9-9a94-f0989d7ae5a4",
                "platform": "www",
                "client_id": "",
            },
            "tracking": {
                "creation_flow": "",
                "creation_point": "https://www.spotify.com/us/signup",
                "referrer": "",
                "origin_vertical": "",
                "origin_surface": "",
            },
        })

        response = self.request_with_retry(
            session, "POST",
            "https://spclient.wg.spotify.com/signup/public/v2/account/validate",
            headers=self.POST_HEADERS,
            data=payload,
            timeout=10,
        )

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        data = response.json()

        if "error" in data and "already_exists" in data["error"]:
            return self.report(True)
        elif "success" in data:
            return self.report(False)

        return self.error(f"Unexpected response body: {data}")
