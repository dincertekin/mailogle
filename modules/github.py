#!/usr/bin/env python3
from rich import print as rprint
import re
import requests

class Github:
    @staticmethod
    def run_scan(email):
        session = requests.Session()

        url = "https://github.com/signup_check/email"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://github.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        csrf_token = Github.get_csrf_token(session, headers)

        data = {
            "value": email,
            "authenticity_token": csrf_token,
        }

        try:
            response = session.post(url, data=data)
            if response.status_code == 422:
                rprint(f"[green][+][/green] [white]GitHub[/white]")
                return True
            elif response.status_code == 200:
                rprint(f"[red][-][/red] [white]GitHub[/white]")
                return False
            elif response.status_code == 429:
                rprint(f"[red]GitHub:[/red] Too many requests.")
                return False
            else:
                rprint(f"[red]GitHub:[/red] Request failed with status code {response.status_code}.")
                return False

        except Exception as e:
            rprint(f"[red]GitHub:[/red] {str(e)}")
            return False

    @staticmethod
    def get_csrf_token(session, headers):
        csrf_token_url = "https://github.com/join"

        csrf_token_regex = re.compile(
            r'<input[^>]+name="authenticity_token"[^>]+value="([^"]+)"'
        )

        response = session.get(csrf_token_url, headers=headers)
        if response.status_code != 200:
            rprint(f"[red]GitHub:[/red] Failed to retrieve join(sign up) page!")
            return False

        match = csrf_token_regex.search(response.text)
        if not match:
            rprint(f"[red]GitHub:[/red] CSRF token not found!")
            return False

        csrf_token = match.group(1)
        return csrf_token
