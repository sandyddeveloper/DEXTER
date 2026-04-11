import asyncio
import sys
import threading
import queue
import psutil
from src.core.brain import brain
from src.perception.listener import listener
from src.config import settings
from src.ui.dashboard import hud_state
from src.ui.window import launch_hud
from src.expression.speaker import speaker
import logging
import time

# Ensure UTF-8 for cool terminal symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich import print as rprint
from src.utils.startup import is_autostart_enabled, enable_autostart
from src.utils.orb_frames import get_orb_frame
import os

def is_model_cached(model_size: str) -> bool:
    """Checks if the faster-whisper model exists in the local HF cache."""
    cache_base = os.path.expanduser("~/.cache/huggingface/hub")
    # Mapping for faster-whisper hub names
    folder_name = f"models--Systran--faster-whisper-{model_size}"
    return os.path.exists(os.path.join(cache_base, folder_name))

# Global queue for HUD text input
external_input_queue = asyncio.Queue()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='stark.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_interaction(user_input, is_proactive=False):
    """Processes a single interaction and updates the HUD."""
    hud_state.current_status = "THINKING"
    if not is_proactive:
        hud_state.chat_history.append({"role": "user", "content": user_input})
    
    response = await brain.chat(user_input)
    hud_state.last_result = response

    hud_state.chat_history.append({"role": "assistant", "content": response})
    hud_state.current_status = "SPEAKING"
    
    # Speak the response
    speaker.speak(response)
    
    hud_state.current_status = "READY"

async def system_guardian():
    """Background thread to monitor system health and act proactively."""
    battery_alerted = False
    
    while True:
        try:
            battery = psutil.sensors_battery()
            if battery:
                # 1. Low Battery Proactive Alert
                if battery.percent < 20 and not battery.power_plugged and not battery_alerted:
                    alert_msg = f"Sir, internal power is at {battery.percent} percent. I recommend connecting a power source or locking the workstation to conserve energy."
                    hud_state.alerts.append(f"CRITICAL: LOW BATTERY ({battery.percent}%)")
                    await run_interaction(alert_msg, is_proactive=True)
                    battery_alerted = True
                elif battery.power_plugged:
                    battery_alerted = False # Reset
                    hud_state.alerts = [a for a in hud_state.alerts if "BATTERY" not in a]

            # 2. Thermal Monitoring (Basic Check)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq and cpu_freq.current > cpu_freq.max * 0.95:
                # High CPU usage alert
                if "THERMAL" not in "".join(hud_state.alerts):
                    hud_state.alerts.append("CRITICAL: THERMAL THROTTLING DETECTED")

            await asyncio.sleep(10) # Check every 10 seconds
        except Exception as e:
            logger.error(f"Guardian error: {e}")
            await asyncio.sleep(5)

async def boot_sequence():
    """Real-world boot sequence for the terminal UI."""
    console = Console()
    
    # ... stark_art remains same ...
    stark_art = """
    [cyan]
    ██████╗ ███████╗██╗  ██╗████████╗███████╗██████╗ 
    ██╔══██╗██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔══██╗
    ██║  ██║█████╗   ╚███╔╝    ██║   █████╗  ██████╔╝
    ██║  ██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██╔══██╗
    ██████╔╝███████╗██╔╝ ██╗   ██║   ███████╗██║  ██║
    ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    [/cyan]
    [bold red]        ::: DEXTER OPERATING SYSTEM V1.1 :::[/bold red]
    """
    console.clear()
    console.print(stark_art)
    
    table = Table(show_header=False, box=None)
    table.add_row("[yellow]SYSTEM:[/yellow]", "STARK INDUSTRIES HUD CORE")
    table.add_row("[yellow]SECURITY:[/yellow]", "ENCRYPTED SESSION ACTIVE")
    table.add_row("[yellow]INTEGRITY:[/yellow]", "REAL-TIME DIAGNOSTICS ACTIVE")
    
    autostart = is_autostart_enabled()
    status_color = "green" if autostart else "red"
    table.add_row("[yellow]AUTO-START:[/yellow]", f"[{status_color}]{'ENABLED' if autostart else 'DISABLED'}[/{status_color}]")
    
    console.print(Panel(table, title="[bold cyan]INITIALIZING NEURAL INTERFACE[/bold cyan]", border_style="cyan"))
    await asyncio.sleep(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        # Phase 1: Global Connectivity (Real Socket Check)
        t1 = progress.add_task("[cyan]Verifying Global Backbone...", total=100)
        import socket
        is_online = False
        try:
            # Check Cloudflare DNS (Very fast and reliable)
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            progress.update(t1, completed=100)
            is_online = True
            
            # Detect primary interface
            import psutil
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters(pernic=True)
            # Find interface with most activity
            best_nic = "WI-FI"
            max_io = 0
            for nic, io in stats.items():
                if nic in interfaces and "loopback" not in nic.lower():
                    if io.bytes_recv > max_io:
                        max_io = io.bytes_recv
                        best_nic = nic.upper()
            hud_state.location_info["interface"] = best_nic
        except:
            progress.update(t1, description="[bold red]CONNECTION OFFLINE[/bold red]", completed=100)
            is_online = False

        # Phase 2: Neural Calibration
        t2 = progress.add_task("[cyan]Connecting Neural Core (Ollama)...", total=100)
        try:
            import ollama
            ollama.list()
            progress.update(t2, completed=100)
        except:
            progress.update(t2, description="[bold red]BEYOND REACH: OFFLINE[/bold red]", completed=100)

        # Phase 3: Rapid Perception (tiny model)
        t3 = progress.add_task("[cyan]Loading Rapid Perception Core...", total=100)
        
        cached = is_model_cached("tiny")
        # Optimization: If cached, force local_files_only even if online for instant boot
        use_local = not is_online or cached
        
        desc = "[cyan]Accessing Neural Archive (Local)..." if cached else "[cyan]Contacting Neural Hub (Network)..."
        progress.update(t3, completed=15, description=desc)
        
        success = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: listener._initialize_model(local_files_only=use_local)
        )
        
        if success:
            final_desc = "[cyan]Rapid Perception: ARCHIVE READY" if cached else "[cyan]Rapid Perception: CORE DOWNLOADED"
            progress.update(t3, description=final_desc, completed=100)
        else:
            fail_desc = "[bold yellow]PERCEPTION OFFLINE (Local Archive Empty)" if not is_online else "[bold yellow]PERCEPTION ERROR"
            progress.update(t3, description=fail_desc, completed=100)

        # Phase 4: Vocal Matrix
        t4 = progress.add_task("[cyan]Synchronizing Vocal Matrix...", total=100)
        progress.update(t4, completed=100)
        await asyncio.sleep(0.5)

    console.print("[bold green]✓ ALL SYSTEMS NOMINAL. ENGAGING LIVE DASHBOARD...[/bold green]")
    await asyncio.sleep(1)

def make_layout() -> Layout:
    """Defines the 3-column dashboard layout."""
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="center", ratio=2),
        Layout(name="right", ratio=1),
    )
    return layout

def generate_dashboard_content(frame_idx: int):
    """Generates the content for each panel of the terminal dashboard."""
    # 1. Header
    header = Panel(
        f"[bold cyan]DEXTER AI ASSISTANCE[/bold cyan] | [red]SYSTEM STATUS: {hud_state.current_status}[/red] | [dim]MARK-85 HUD CORE[/dim]",
        border_style="cyan"
    )

    # 2. Left Panel: Vitals
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    vitals_table = Table(show_header=False, box=None, padding=0)
    vitals_table.add_row(f"[yellow]CPU:[/yellow] {cpu_usage}%")
    vitals_table.add_row(f"[cyan][{'█' * int(cpu_usage/10)}{' '*(10-int(cpu_usage/10))}][/cyan]")
    vitals_table.add_row(f"[yellow]RAM:[/yellow] {ram_usage}%")
    vitals_table.add_row(f"[cyan][{'█' * int(ram_usage/10)}{' '*(10-int(ram_usage/10))}][/cyan]")
    vitals_table.add_row("")
    vitals_table.add_row("[bold]PREVIOUS HISTORY[/bold]")
    for item in hud_state.search_history[:4]:
        vitals_table.add_row(f"- {item['query'][:12]} [dim]({item['score']}%)[/dim]")
    
    left_panel = Panel(vitals_table, title="[bold]SYSTEM VITALS[/bold]", border_style="blue")

    # 3. Center Panel: Neural Orb
    orb_text = get_orb_frame(hud_state.current_status, frame_idx)
    center_panel = Panel(
        f"\n{orb_text}\n\n[bold cyan]{hud_state.current_status}[/bold cyan]",
        title="[bold red]NEURAL CORE[/bold red]",
        border_style="red"
    )

    # 4. Right Panel: Action Results
    results_table = Table(show_header=False, box=None)
    results_table.add_row("[bold cyan]LAST COMMAND[/bold cyan]")
    results_table.add_row(f"[dim]{hud_state.last_command}[/dim]")
    results_table.add_row("")
    results_table.add_row("[bold cyan]EXECUTION LOG[/bold cyan]")
    results_table.add_row(f"[green]{hud_state.last_result[:80]}[/green]")
    results_table.add_row("")
    results_table.add_row(f"[yellow]LOCATION:[/yellow] {hud_state.location_info['city']}")
    
    right_panel = Panel(results_table, title="[bold]CMD INSIGHTS[/bold]", border_style="blue")

    # 5. Footer
    footer = Panel(
        f"[dim]READY FOR COMMAND SOURCE... | TYPE OR SPEAK |[/dim] [bold red]{hud_state.location_info['city'].upper()}[/bold red]",
        border_style="cyan"
    )

    return header, left_panel, center_panel, right_panel, footer

async def orchestrator_loop():
    """Main background loop for listening and processing."""
    try:
        await boot_sequence()
        guardian_task = asyncio.create_task(system_guardian())
        
        # Silently upgrade perception model in background
        asyncio.get_event_loop().run_in_executor(None, lambda: listener.upgrade_model(local_files_only=hud_state.is_online == False))
        
        layout = make_layout()
        frame_idx = 0
        
        with Live(layout, refresh_per_second=10, screen=True) as live:
            while True:
                try:
                    # Update Layout Content
                    h, l, c, r, f = generate_dashboard_content(frame_idx)
                    layout["header"].update(h)
                    layout["left"].update(l)
                    layout["center"].update(c)
                    layout["right"].update(r)
                    layout["footer"].update(f)
                    frame_idx += 1

                    # AI Logic (Priority: HUD Text Input)
                    try:
                        text_cmd = external_input_queue.get_nowait()
                        hud_state.last_command = text_cmd
                        await run_interaction(text_cmd)
                        continue
                    except asyncio.QueueEmpty: pass

                    hud_state.current_status = "STANDBY"
                    
                    # Check Perception Readiness
                    if not listener.is_ready:
                        # Asyncly try to initialize in background if not ready
                        asyncio.get_event_loop().run_in_executor(None, listener._initialize_model)
                        hud_state.current_status = "OFFLINE"
                    
                    # Background wake word detection (Only if listener is ready)
                    if listener.is_ready:
                        if await asyncio.get_event_loop().run_in_executor(None, listener.listen_for_wake_word):
                            hud_state.current_status = "LISTENING"
                            command = await asyncio.get_event_loop().run_in_executor(None, listener.listen_to_command)
                            if command:
                                hud_state.last_command = command
                                await run_interaction(command)
                    
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Orchestrator error: {e}")
                    await asyncio.sleep(1)
    finally:
        # Cleanup
        logger.info("DEXTER systems shutting down...")
        try:
            guardian_task.cancel()
            await guardian_task
        except: pass

def start_backend():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(orchestrator_loop())
    finally:
        loop.close()

if __name__ == "__main__":
    # Ensure dependencies or settings are right if needed
    # (Optional: silently enable autostart if first run)
    
    # Start Orchestrator (Backend) in a thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Launch GUI (Blocks main thread)
    launch_hud()
