#!/usr/bin/env python3
import json

from modules.base import BaseModule, register


@register
class Netflix(BaseModule):
    name = "Netflix"

    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.netflix.com",
        "Referer": "https://www.netflix.com/",
    }

    def check(self, email):
        session = self.create_session()
        session.headers.update(self.BASE_HEADERS)

        try:
            session.get("https://www.netflix.com/", timeout=10, allow_redirects=True)
        except Exception as e:
            return self.error(f"Failed to load Netflix homepage: {e}")

        flwssn = session.cookies.get("flwssn")
        if not flwssn:
            return self.error("Session token (flwssn) not found. IP may be flagged.")

        graphql_headers = {
            **self.BASE_HEADERS,
            "content-type": "application/json",
            "x-netflix.context.operation-name": "CLCSWebInitSignup",
            "x-netflix.request.clcs.bucket": "high",
        }

        payload = json.dumps({
            "operationName": "CLCSWebInitSignup",
            "variables": {
                "inputUserJourneyNode": "WELCOME",
                "locale": "en-US",
                "inputFields": [
                    {"name": "flwssn", "value": {"stringValue": flwssn}},
                    {"name": "email", "value": {"stringValue": email}},
                ],
            },
            "extensions": {
                "persistedQuery": {
                    "id": "f6e8ddc6-79fb-4ff2-8e55-893d707887a4",
                    "version": 102,
                }
            },
        })

        response = self.request_with_retry(
            session, "POST",
            "https://web.prod.cloud.netflix.com/graphql",
            headers=graphql_headers,
            data=payload,
            timeout=10,
        )

        if response.status_code == 429:
            return self.error("Rate limited. Try again later.")

        if response.status_code != 200:
            return self.error(f"Request failed with status {response.status_code}.")

        body = response.text

        if "Welcome back!" in body:
            return self.report(True)

        if "sign-up link" in body or "create your account" in body:
            return self.report(False)

        if '"errors"' in body:
            return self.error(f"GraphQL error in response: {body[:200]}")

        return self.error(f"Unexpected response body: {body[:200]}")
