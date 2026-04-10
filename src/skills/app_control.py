import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def open_chrome():
    """Opens Google Chrome."""
    try:
        # Standard path for Windows
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            # Try 86 bit path
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path])
            return "Launching Chrome, sir."
        else:
            # Fallback to just 'chrome' if in PATH
            subprocess.Popen(["start", "chrome"], shell=True)
            return "Searching for Chrome in your PATH and launching, sir."
    except Exception as e:
        logger.error(f"Failed to open Chrome: {e}")
        return "I am unable to launch Chrome at the moment."

def open_vscode():
    """Opens Visual Studio Code."""
    try:
        # VS Code is usually in PATH as 'code'
        subprocess.Popen(["code"], shell=True)
        return "Initializing Visual Studio Code environments, sir."
    except Exception as e:
        logger.error(f"Failed to open VS Code: {e}")
        return "I couldn't initialize the code environment."

# Mapping for the brain to use
SKILLS = {
    "open_chrome": open_chrome,
    "open_vscode": open_vscode
}
