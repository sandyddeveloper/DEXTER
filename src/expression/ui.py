from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.progress import BarColumn, Progress
import psutil
from datetime import datetime
from src.config import settings
import time
import math
import ctypes

# Windows Console Constants
STD_OUTPUT_HANDLE = -11
CONSOLE_FULLSCREEN_MODE = 1

console = Console()

class FrequencyWave:
    def __init__(self):
        self.phase = 0
        
    def __rich__(self) -> Text:
        self.phase += 0.5
        width = 40
        wave = ""
        for x in range(width):
            # Oscilloscope / Frequency wave effect
            y = int(3 * math.sin(x * 0.4 + self.phase)) + 3
            wave += " " * y + "•" + " " * (7 - y) + "\n"
        
        # Alternative: Horizontal wave
        h_wave = ""
        chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        for x in range(30):
            val = int(4 * math.sin(x * 0.5 + self.phase) + 4)
            h_wave += chars[val]
            
        return Text(h_wave, style="bold cyan")

class VisualEngine:
    def __init__(self):
        self.layout = Layout()
        self.chat_history = []
        self.status = "STANDING BY"
        self.wave = FrequencyWave()
        self.start_time = time.time()
        
        # Setup Layout
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["body"].split_row(
            Layout(name="main", ratio=3),
            Layout(name="side", ratio=1)
        )
        self.layout["side"].split_column(
            Layout(name="visual", size=10),
            Layout(name="stats", ratio=1)
        )

    def get_header(self):
        uptime = int(time.time() - self.start_time)
        header_text = f"[bold cyan]DEXTER OS v1.1[/] | Uptime: {uptime}s | {datetime.now().strftime('%H:%M:%S')}"
        return Panel(header_text, style="cyan")

    def get_footer(self):
        color = "green" if "LISTENING" in self.status else "cyan"
        if "THINKING" in self.status: color = "yellow"
        return Panel(Text(f"STATUS: {self.status}", style=f"bold {color}"), style="cyan")

    def get_stats(self):
        table = Table.grid(expand=True)
        # CPU
        cpu = psutil.cpu_percent()
        table.add_row(f"CPU: [cyan]{cpu}%[/]")
        # RAM
        ram = psutil.virtual_memory().percent
        table.add_row(f"RAM: [cyan]{ram}%[/]")
        # Network
        net = psutil.net_io_counters()
        sent = net.bytes_sent / (1024 * 1024)
        recv = net.bytes_recv / (1024 * 1024)
        table.add_row(f"NET ↓: [cyan]{recv:.1f} MB[/]")
        table.add_row(f"NET ↑: [cyan]{sent:.1f} MB[/]")
        # Disk
        disk = psutil.disk_io_counters()
        read = disk.read_bytes / (1024 * 1024)
        table.add_row(f"DISK: [cyan]{read:.1f} MB[/]")
        
        return Panel(table, title="[bold]SYSTEM MONITOR[/]", border_style="blue")

    def get_main(self):
        chat_text = Text()
        for role, msg in self.chat_history[-10:]:
            color = "cyan" if role == "DEXTER" else "green"
            chat_text.append(f"{role}: ", style=f"bold {color}")
            chat_text.append(f"{msg}\n", style="white")
        
        return Panel(chat_text, title="[bold]CONSOLE[/]", border_style="cyan")

    def update_layout(self):
        self.layout["header"].update(self.get_header())
        self.layout["footer"].update(self.get_footer())
        self.layout["main"].update(self.get_main())
        self.layout["stats"].update(self.get_stats())
        self.layout["visual"].update(Panel(self.wave, title="AI CORE", border_style="cyan"))
        return self.layout

    def add_chat(self, role, message):
        self.chat_history.append((role, message))

    def set_status(self, status):
        self.status = status.upper()

    def enable_fullscreen(self):
        """Forces the Windows console into fullscreen mode."""
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            # 1 = Fullscreen, 2 = Windowed
            kernel32.SetConsoleDisplayMode(handle, CONSOLE_FULLSCREEN_MODE, ctypes.byref(ctypes.c_ulong()))
            # Also set title
            kernel32.SetConsoleTitleW(f"{settings.ASSISTANT_NAME} OS v1.1 - SECURE SESSION")
        except Exception:
            pass # Fallback for non-windows or restricted environments

    def show_boot_sequence(self):
        self.enable_fullscreen()
        console.clear()
        checks = [
            "INITIALIZING NEURAL CORE...",
            "LOADING WHISPER PERCEPTION MODULES...",
            "CONNECTING TO OLLAMA INTELLIGENCE LAYER...",
            "CALIBRATING AUDIO SENSORS...",
            "ESTABLISHING SECURE LOCAL STORAGE...",
            "STARTING DEXTER OS V1.1..."
        ]
        
        with Progress(
            "{task.description}",
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=console
        ) as progress:
            for check in checks:
                task = progress.add_task(f"[cyan]{check}", total=100)
                for _ in range(10):
                    time.sleep(0.1)
                    progress.update(task, advance=10)
        
        time.sleep(0.5)
        console.clear()

ui = VisualEngine()
