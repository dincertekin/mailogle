#!/usr/bin/env python3
from pyfiglet import Figlet
from rich import print as rprint
from rich.prompt import Prompt
from tabulate import tabulate
import argparse
import importlib
import os
import sys
import time

# ./modules/*
def load_modules():
    module_mapping = {}
    for filename in os.listdir('modules'):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, module_name.capitalize()):
                module_class = getattr(module, module_name.capitalize())
                module_mapping[module_name] = module_class
            else:
                rprint(f"[red]Warning:[/red] [white]Module '{module_name}' does not have the class.[/white]")
    return module_mapping

def main():
    parser = argparse.ArgumentParser(
        prog='mailogle',
        description='A simple tool for email OSINT.',
        epilog='For more info, visit: github.com/dincertekin/mailogle'
    )

    parser.add_argument('-m', '--module', help='Specify the module to use (e.g., instagram, snapchat, spotify)')
    parser.add_argument('mail', help='Email address to scan')
    args = parser.parse_args()

    email_confirm = Prompt.ask(f"[green]{args.mail}[/green] is that correct? [pink](y/n)[/pink]", default="y")
    if email_confirm.lower() not in ["y", "yes"]:
        rprint("[red]Error:[/red] [white]Please run the program again with the correct email.[/white]")
        sys.exit(1)

    f = Figlet(font='slant')
    print(f.renderText('mailogle'))

    rprint("[bold green]Scanning the email...[/bold green]")

    animation = "|/-\\"
    start_time = time.time()
    while True:
        for i in range(len(animation)):
            time.sleep(0.2)
            sys.stdout.write("\r" + animation[i % len(animation)])
            sys.stdout.flush()
        if time.time() - start_time > 3: # Run for 3 seconds
            break
    sys.stdout.write("\r")

    print(tabulate([[args.mail]], headers=["Email"], tablefmt="grid"))

    module_mapping = load_modules()
    if args.module:
        if args.module in module_mapping:
            module_class = module_mapping[args.module]
            module_instance = module_class()
            rprint(f"Running scan for [yellow]{args.module}[/yellow]...")
            module_instance.run_scan(args.mail)
        else:
            rprint(f"[red]Error:[/red] [white]Module '{args.module}' not found![/white]")
            sys.exit(1)
    else:
        for module_name, module_class in module_mapping.items():
            module_instance = module_class()
            module_instance.run_scan(args.mail)

if __name__ == "__main__":
    main()
