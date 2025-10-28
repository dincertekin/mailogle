#!/usr/bin/env python3
from rich import print as rprint
import re
import requests

class Hudsonrock:
    @staticmethod
    def run_scan(email):
        session = requests.Session()

        url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={email}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }

        try:
            response = session.get(url, headers=headers)
            data = response.json()

            if data.get("stealers") == [] and data.get("total_corporate_services") == 0 and data.get("total_user_services") == 0:
                rprint(f"[red][-][/red] [white]HudsonRock[/white]")
                return False
            else:

                rprint(f"[green][+][/green] [white]HudsonRock[/white]")
                return True

        except Exception as e:
            rprint(f"[red]HudsonRock:[/red] {str(e)}")
            return False
