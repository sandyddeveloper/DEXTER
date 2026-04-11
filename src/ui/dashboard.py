from fastapi import FastAPI, Request
from src.perception.listener import listener
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psutil
import GPUtil
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="src/ui/templates")

import aiohttp
import asyncio

class HUDState:
    chat_history = []
    current_status = "STANDING BY"
    start_time = time.time()
    alerts = []
    
    # Premium UI Data
    location_info = {"city": "DETECTING...", "lat": 0, "lon": 0}
    last_command = "WAITING FOR INPUT"
    last_result = "SYSTEMS NOMINAL"
    search_history = [
        {"query": "WEATHER", "score": 85},
        {"query": "MEDICAL", "score": 45},
        {"query": "TRAFFIC", "score": 30}
    ]
    info_card = {"type": "none", "title": "", "content": {}}
    
    # Real-time Telemetry state
    last_net_stats = psutil.net_io_counters()
    last_net_time = time.time()
    current_speeds = {"down": 0.0, "up": 0.0}
    is_online = True

hud_state = HUDState()

@app.get("/api/control")
async def sys_control(action: str):
    """Executes system-level primitive commands from the HUD."""
    from src.skills.system_control import SYSTEM_SKILLS
    if action == "lock":
        SYSTEM_SKILLS["lock_pc"]()
    elif action == "mute":
        SYSTEM_SKILLS["set_volume"](0)
    elif action == "purge":
        hud_state.chat_history = []
    elif action == "shutdown":
        SYSTEM_SKILLS["shutdown_assistant"]()
    return {"ok": True}

async def connection_manager():
    """Periodically checks internet connectivity and updates location."""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://ip-api.com/json', timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        hud_state.location_info = {
                            "city": data.get("city", "Unknown"),
                            "lat": data.get("lat", 0),
                            "lon": data.get("lon", 0),
                            "isp": data.get("isp", "LOCAL NETWORK"),
                            "status": "success"
                        }
                        hud_state.is_online = True
                        logger.info(f"Connectivity verified: {hud_state.location_info['city']}")
                    else:
                        hud_state.is_online = False
        except Exception as e:
            hud_state.is_online = False
            hud_state.location_info["isp"] = "LOCAL ARCHIVE"
            logger.warning(f"Connectivity offline: {e}")
        
        await asyncio.sleep(60) # Check every minute

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(connection_manager())

@app.get("/")
async def get_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/telemetry")
async def get_telemetry():
    """Returns real-time system diagnostics with safety fallbacks."""
    try:
        net = psutil.net_io_counters()
        disk = psutil.disk_io_counters()
        battery = psutil.sensors_battery()
        
        gpu_data = {"load": 0, "mem": 0}
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_data["load"] = gpus[0].load * 100
                gpu_data["mem"] = gpus[0].memoryUtil * 100
        except: pass

        # Network Speed Calculation
        now = time.time()
        dt = now - hud_state.last_net_time
        if dt > 0:
            hud_state.current_speeds["down"] = round(((net.bytes_recv - hud_state.last_net_stats.bytes_recv) * 8) / (dt * 1024 * 1024), 2)
            hud_state.current_speeds["up"] = round(((net.bytes_sent - hud_state.last_net_stats.bytes_sent) * 8) / (dt * 1024 * 1024), 2)
            
            hud_state.last_net_stats = net
            hud_state.last_net_time = now

        # Proactive Detection (If boot was too fast or failed)
        if hud_state.location_info.get("interface") == "DETECTING...":
            try:
                interfaces = psutil.net_if_addrs()
                stats = psutil.net_io_counters(pernic=True)
                best_nic = "WI-FI"
                max_io = 0
                for nic, io in stats.items():
                    if nic in interfaces and "loopback" not in nic.lower():
                        if io.bytes_recv > max_io:
                            max_io = io.bytes_recv
                            best_nic = nic.upper()
                hud_state.location_info["interface"] = best_nic
            except: pass

        if not hud_state.is_online:
            hud_state.current_status = "OFFLINE"
        elif hud_state.current_status == "OFFLINE":
            hud_state.current_status = "READY"

        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "gpu": round(gpu_data["load"], 1),
            "gpu_mem": round(gpu_data["mem"], 1),
            "net_recv_total": round(net.bytes_recv / (1024 * 1024), 2),
            "net_sent_total": round(net.bytes_sent / (1024 * 1024), 2),
            "net_down": hud_state.current_speeds["down"],
            "net_up": hud_state.current_speeds["up"],
            "disk_usage": psutil.disk_usage('/').percent,
            "disk_io": round((disk.read_bytes + disk.write_bytes) / (1024 * 1024), 2),
            "battery": battery.percent if battery else 100,
            "uptime": int(time.time() - hud_state.start_time),
            "status": hud_state.current_status,
            "is_online": hud_state.is_online,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "has_alert": len(hud_state.alerts) > 0,
            "location": hud_state.location_info,
            "active_nic": hud_state.location_info.get("interface", "DETECTING..."),
            "neural_model": listener.model_path.upper() if hasattr(listener, 'model_path') else "TINY",
            "last_cmd": hud_state.last_command,
            "last_res": hud_state.last_result,
            "history": hud_state.search_history,
            "info_card": hud_state.info_card
        }
    except Exception as e:
        logger.error(f"Telemetry API error: {e}")
        # Complete fallback dictionary to prevent frontend crashes
        return {
            "status": "INITIALIZING...", 
            "is_online": False,
            "cpu": 0, 
            "ram": 0, 
            "gpu": 0,
            "gpu_mem": 0,
            "net_down": 0.0, 
            "net_up": 0.0, 
            "disk_usage": 0,
            "active_nic": "WAITING...", 
            "neural_model": "LOAD",
            "last_cmd": "WAITING...",
            "last_res": "RECOVERING SYSTEMS...",
            "location": {"city": "OFFLINE", "isp": "LOCAL NETWORK"},
            "history": [],
            "info_card": {"type": "none"}
        }

@app.get("/api/chat")
async def get_chat():
    return {"history": hud_state.chat_history[-15:], "alerts": hud_state.alerts}

@app.post("/api/send_text")
async def send_text(text: str):
    """Allows triggering commands from HUD text input."""
    # We will implement a global queue in main.py to handle this
    from src.main import external_input_queue
    external_input_queue.put_nowait(text)
    return {"ok": True}

def run_server():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
