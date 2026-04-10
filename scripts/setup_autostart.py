import os
import sys
import winreg as reg

def add_to_startup():
    # Path to the current script or a batch file that starts DEXTER
    # We'll create a starter.bat in the root for simplicity
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bat_path = os.path.join(base_dir, "start_dexter.bat")
    
    # Use the current python interpreter (to ensure it stays in the venv)
    python_exe = sys.executable
    
    # Create a JARVIS-style batch file that opens a visible terminal
    with open(bat_path, "w") as f:
        f.write("@echo off\n")
        f.write(f"title DEXTER - Systems Initializing...\n")
        f.write("color 0b\n")  # Cyan text on black background for JARVIS feel
        f.write(f"cd /d \"{base_dir}\"\n")
        f.write(f"\"{python_exe}\" -m src.main\n")
        f.write("pause\n")

    # Registry key for startup
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "DEXTER_AI"
    
    # Wrap in cmd /c start to ensure a window pops up
    command = f'cmd /c start "DEXTER OS" /max "{bat_path}"'
    
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, app_name, 0, reg.REG_SZ, command)
        reg.CloseKey(key)
        print(f"Successfully added DEXTER to startup with visible UI.")
        print(f"Target: {command}")
    except Exception as e:
        print(f"Failed to add to startup: {e}")

if __name__ == "__main__":
    add_to_startup()
