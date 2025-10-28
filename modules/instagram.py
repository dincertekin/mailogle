#!/usr/bin/env python3
from bs4 import BeautifulSoup
from rich import print as rprint
import random
import requests
import string

class Instagram:
    @staticmethod
    def run_scan(email):
        session = requests.Session()

        url = "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/"

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        ]

        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.instagram.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        try:
            headers["x-csrftoken"] = Instagram.get_csrf_token(session, headers)

            data = {
                'email': email,
                'username': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),
                'first_name': '',
                'opt_into_one_tap': 'false'
            }

            response = session.post(url, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    if 'email' in data['errors']:
                        if data['errors']['email'][0]['code'] == 'email_is_taken':
                            return rprint(f"[green][+][/green] [white]Instagram[/white]")
                        elif "email_sharing_limit" in str(data["errors"]):
                            return rprint(f"[green][+][/green] [white]Instagram[/white] [blue](sharing limit reached)[/blue]")
                        else:
                            return rprint(f"[red][-][/red] [white]Instagram[/white]")
                else:
                    return rprint(f"[red][-][/red] [white]Instagram[/white]")
            else:
                return rprint(f"[red]Instagram:[/red] [white]Request failed with status code {response.status_code}.[/white]")
        except Exception as e:
            return rprint(f"[red]Instagram:[/red] [white]{str(e)}[/white]")

    @staticmethod
    def get_csrf_token(session, headers):
        csrf_token_url = "https://www.instagram.com/accounts/login/"

        response = session.get(csrf_token_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            csrf_token = None
            for script in scripts:
                if 'csrf_token' in script.text:
                    csrf_token = script.text.split('csrf_token":"')[1].split('"')[0]
                    break

            if not csrf_token:
                rprint("[red]Instagram:[/red] CSRF token not found in login page!")
                return False

            return csrf_token
        else:
            rprint(f"[red]Instagram:[/red] Failed to retrieve login page!")
            return False