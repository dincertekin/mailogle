#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyfiglet import Figlet
from rich import print as rprint
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from tabulate import tabulate
import argparse
import csv
import importlib
import json
import os
import re
import sys

from modules.base import MODULES

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

STATUS_LABELS = {
    True: "[green][+] Found[/green]",
    False: "[red][-] Not found[/red]",
    None: "[yellow][!] Error[/yellow]",
}


def load_modules():
    for filename in os.listdir('modules'):
        if filename.endswith('.py') and not filename.startswith('_'):
            importlib.import_module(f'modules.{filename[:-3]}')
    return MODULES


def run_modules(module_mapping, email):
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[bold green]Scanning the email...", total=len(module_mapping))
        with ThreadPoolExecutor(max_workers=max(len(module_mapping), 1)) as executor:
            futures = [executor.submit(module_class().run_scan, email) for module_class in module_mapping.values()]
            for future in as_completed(futures):
                results.append(future.result())
                progress.advance(task)
    return results


def render_results_table(results):
    table = Table(title="Scan Results")
    table.add_column("Module")
    table.add_column("Status")
    table.add_column("Notes", style="dim")

    for result in sorted(results, key=lambda r: r.name.lower()):
        table.add_row(result.name, STATUS_LABELS[result.found], result.detail or "")

    rprint(table)


def export_results(email, results, fmt):
    filename = f"{re.sub(r'[^A-Za-z0-9]+', '_', email)}_results.{fmt}"

    if fmt == 'json':
        payload = {
            "email": email,
            "results": [{"module": r.name, "found": r.found, "detail": r.detail} for r in results],
        }
        with open(filename, 'w') as f:
            json.dump(payload, f, indent=2)
    else:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["module", "found", "detail"])
            for result in results:
                writer.writerow([result.name, result.found, result.detail or ""])

    rprint(f"[green]Results exported to[/green] [white]{filename}[/white]")


def main():
    parser = argparse.ArgumentParser(
        prog='mailogle',
        description='A simple tool for email OSINT.',
        epilog='For more info, visit: github.com/dincertekin/mailogle'
    )

    parser.add_argument('-m', '--module', help='Specify the module to use (e.g., instagram, snapchat, spotify)')
    parser.add_argument('-l', '--list-modules', action='store_true', help='List the available modules and exit')
    parser.add_argument('-o', '--output', choices=['json', 'csv'], help='Export results to a file in the given format')
    parser.add_argument('mail', nargs='?', help='Email address to scan')
    args = parser.parse_args()

    module_mapping = load_modules()

    if args.list_modules:
        print(tabulate([[name] for name in sorted(module_mapping)], headers=["Module"], tablefmt="grid"))
        sys.exit(0)

    if not args.mail:
        parser.error('the following arguments are required: mail')

    if not EMAIL_REGEX.match(args.mail):
        rprint("[red]Error:[/red] [white]That doesn't look like a valid email address.[/white]")
        sys.exit(1)

    if args.module and args.module not in module_mapping:
        rprint(f"[red]Error:[/red] [white]Module '{args.module}' not found![/white]")
        sys.exit(1)

    email_confirm = Prompt.ask(f"[green]{args.mail}[/green] is that correct? [pink](y/n)[/pink]", default="y")
    if email_confirm.lower() not in ["y", "yes"]:
        rprint("[red]Error:[/red] [white]Please run the program again with the correct email.[/white]")
        sys.exit(1)

    f = Figlet(font='slant')
    banner = f.renderText('mailogle').rstrip('\n')
    width = max(len(line) for line in banner.splitlines())

    rprint(f"[bold green]{banner}[/bold green]")
    rprint(f"[dim]{'github.com/dincertekin/mailogle'.center(width)}[/dim]\n")

    rprint(Panel(f"[bold]{args.mail}[/bold]", title="Target", border_style="green", expand=False))

    targets = {args.module: module_mapping[args.module]} if args.module else module_mapping
    results = run_modules(targets, args.mail)

    render_results_table(results)

    if args.output:
        export_results(args.mail, results, args.output)


if __name__ == "__main__":
    main()
