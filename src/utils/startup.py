import os
import sys
import winreg as reg
import logging

logger = logging.getLogger(__name__)

def is_autostart_enabled(app_name="DEXTER_AI"):
    """Checks if the app is already in the Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
        value, _ = reg.QueryValueEx(key, app_name)
        reg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking autostart: {e}")
        return False

def enable_autostart(app_name="DEXTER_AI"):
    """Adds the start_dexter.bat to the Windows startup registry."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bat_path = os.path.join(base_dir, "start_dexter.bat")
    
    if not os.path.exists(bat_path):
        logger.error(f"Cannot enable autostart: {bat_path} not found.")
        return False

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # command = f'cmd /c start "DEXTER OS" /max "{bat_path}"'
    # Improved command: use cmd /c and quote the path correctly
    command = f'cmd /c "{bat_path}"'
    
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, app_name, 0, reg.REG_SZ, command)
        reg.CloseKey(key)
        logger.info(f"Autostart enabled: {command}")
        return True
    except Exception as e:
        logger.error(f"Failed to enable autostart: {e}")
        return False

def disable_autostart(app_name="DEXTER_AI"):
    """Removes the app from the Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.DeleteValue(key, app_name)
        reg.CloseKey(key)
        logger.info("Autostart disabled.")
        return True
    except FileNotFoundError:
        return True # Already disabled
    except Exception as e:
        logger.error(f"Failed to disable autostart: {e}")
        return False
