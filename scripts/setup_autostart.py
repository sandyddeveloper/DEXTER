import os
import sys

# Add src to path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.startup import enable_autostart, is_autostart_enabled

def setup():
    print("--- DEXTER System Integration: Auto-Start ---")
    if is_autostart_enabled():
        print("[INFO] Auto-start is already configured.")
        # Re-enable to ensure path is correct
        if enable_autostart():
            print("[SUCCESS] Startup entry verified and updated.")
    else:
        print("[INFO] Enabling auto-start for DEXTER...")
        if enable_autostart():
            print("[SUCCESS] DEXTER will now launch on system boot.")
        else:
            print("[ERROR] Failed to enable auto-start.")

if __name__ == "__main__":
    setup()
