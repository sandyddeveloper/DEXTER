from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from src.config import settings

console = Console()

class DEXTERUI:
    def __init__(self):
        self.assistant_name = settings.ASSISTANT_NAME
        
    def show_welcome(self):
        welcome_text = Text()
        welcome_text.append(f"[{self.assistant_name}] ", style="bold cyan")
        welcome_text.append("Systems online. All modules operational.\n", style="italic gray")
        welcome_text.append("Awaiting your command, sir.", style="bold white")
        
        console.print(Panel(welcome_text, title=f"{self.assistant_name} OS v1.0", border_style="cyan"))

    def print_assistant(self, message: str):
        console.print(f"\n[bold cyan]{self.assistant_name}:[/] [white]{message}[/]")

    def print_user(self, message: str):
        console.print(f"\n[bold green]YOU:[/] [white]{message}[/]")

    def show_status(self, status: str):
        console.print(f"[italic gray]>>> {status}...[/]")

    def print_error(self, message: str):
        console.print(f"\n[bold red]ERROR:[/] [white]{message}[/]")

ui = DEXTERUI()
