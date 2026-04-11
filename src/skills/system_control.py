import os
import subprocess
import webbrowser
import ctypes
import logging
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc

logger = logging.getLogger(__name__)

def set_volume(level: int):
    """Sets the system volume (0-100)."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        # Convert 0-100 to 0.0-1.0
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Adjusting system volume to {level} percent, sir."
    except Exception as e:
        logger.error(f"Volume error: {e}")
        return "I am unable to access the audio hardware at this time."

def set_brightness(level: int):
    """Sets the screen brightness (0-100)."""
    try:
        sbc.set_brightness(level)
        return f"Display luminance adjusted to {level} percent."
    except Exception as e:
        logger.error(f"Brightness error: {e}")
        return "The display drivers are not responding to my requests."

def search_web(query: str, engine: str = "google"):
    """Searches the web for a query."""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching the data streams for '{query}', sir."
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return "I encountered an error while browsing the web."

def lock_pc():
    """Locks the Windows workstation. Requires confirmation in main loop!"""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Locking workstation. DEXTER session secured."
    except Exception as e:
        logger.error(f"Lock error: {e}")
        return "Security protocol failed. Please lock your workstation manually."

def control_media(action: str):
    """Controls media playback (play, pause, next, prev)."""
    try:
        # VK codes: Play/Pause = 0xB3, Next = 0xB0, Prev = 0xB1
        vk_map = {"play": 0xB3, "pause": 0xB3, "next": 0xB0, "prev": 0xB1, "stop": 0xB2}
        if action in vk_map:
            ctypes.windll.user32.keybd_event(vk_map[action], 0, 0, 0)
            return f"Media command '{action}' executed."
    except Exception as e:
        logger.error(f"Media error: {e}")
        return "Media interface is not responding."

def shutdown_assistant():
    """Exits the DEXTER assistant process."""
    try:
        import threading
        import time
        import os
        
        def delayed_kill():
            time.sleep(2.5) # Wait for speech to finish
            os._exit(0)
            
        threading.Thread(target=delayed_kill, daemon=True).start()
        return "Shutting down all systems. Powering off. Goodbye, sir."
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        return "I am unable to terminate my processes, sir."

def get_weather(location=None):
    """Fetches real-time weather information for the specified location or current city."""
    from src.ui.dashboard import hud_state
    import requests
    
    city = location if location else hud_state.location_info.get("city", "London")
    try:
        # Use wttr.in for clean JSON
        resp = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            curr = data['current_condition'][0]
            temp = curr['temp_C']
            desc = curr['weatherDesc'][0]['value']
            humidity = curr['humidity']
            wind = curr['windspeedKmph']
            
            # Update HUD Info Card
            hud_state.info_card = {
                "type": "weather",
                "title": f"Weather in {city}",
                "content": {
                    "temp": temp,
                    "desc": desc,
                    "humidity": f"{humidity}%",
                    "wind": f"{wind} km/h"
                }
            }
            return f"The current weather in {city} is {desc} at {temp} degrees Celsius, with {humidity} percent humidity."
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return "I am unable to retrieve the climate data at this moment, sir."

# Tool Registry for the Brain
SYSTEM_SKILLS = {
    "set_volume": set_volume,
    "set_brightness": set_brightness,
    "search_web": search_web,
    "lock_pc": lock_pc,
    "control_media": control_media,
    "shutdown_assistant": shutdown_assistant,
    "get_weather": get_weather
}
