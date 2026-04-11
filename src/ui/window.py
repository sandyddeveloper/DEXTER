import webview
import threading
from src.ui.dashboard import run_server
import time
import sys
import os
import winsound

class StarkApi:
    """API for the HUD to communicate with the Python Window Manager."""
    def __init__(self, window):
        self._window = window
        self._is_widget = False

    def toggle_fullscreen(self):
        self._window.toggle_fullscreen()
        return "Toggled Fullscreen"

    def toggle_on_top(self):
        # pywebview currently doesn't allow toggling 'on_top' post-creation easily
        # but we can simulate it or restart if needed. 
        # For now we provide a 'Widget Mode' resize.
        return "On Top Toggle [Dev Note: Requires Reload]"

    def minimize(self):
        self._window.minimize()

    def close(self):
        self._window.destroy()
        os._exit(0)

class StarkWindow:
    def __init__(self):
        self.url = "http://127.0.0.1:8000"
        self.window = None

    def play_boot_sound(self):
        try:
            winsound.Beep(400, 100)
            winsound.Beep(600, 100)
            winsound.Beep(1200, 300)
        except: pass

    def start(self, fullscreen=True, frameless=True, on_top=True):
        # 1. Start Backend
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)
        
        # 2. Sound
        self.play_boot_sound()

        # 3. Create Window and Attach API
        api = StarkApi(None) # Window reference will be set after creation
        self.window = webview.create_window(
            'STARK HUD - DEXTER OS', 
            self.url,
            fullscreen=fullscreen,
            frameless=frameless,
            on_top=on_top,
            background_color='#070707',
            width=1200,
            height=800,
            js_api=api
        )
        api._window = self.window
        
        webview.start()

def launch_hud():
    hud = StarkWindow()
    # Support for mode arguments
    is_windowed = "--windowed" in sys.argv
    is_widget = "--widget" in sys.argv
    
    if is_widget:
        # Widget mode: Small, bottom-right corner, always on top
        # We try to get screen size to position it
        width, height = 350, 550
        try:
            screen = webview.screens[0]
            x = screen.width - width - 20
            y = screen.height - height - 60 # Leave some space for taskbar
        except:
            x, y = None, None
            
        hud.start(fullscreen=False, frameless=True, on_top=True)
        if hud.window:
            hud.window.resize(width, height)
            if x is not None:
                hud.window.move(x, y)
    else:
        # Default to Fullscreen, Frameless, and On-Top (OS/Widget style)
        hud.start(fullscreen=not is_windowed, frameless=True, on_top=not is_windowed)

if __name__ == "__main__":
    launch_hud()
