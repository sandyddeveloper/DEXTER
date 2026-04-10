import psutil
import platform
from datetime import datetime

def get_system_status():
    """
    Returns a summary of the current system status.
    """
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    status = (
        f"CPU Usage: {cpu_usage}%\n"
        f"Memory Usage: {memory.percent}%\n"
    )
    
    if battery:
        status += f"Battery: {battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}\n"
        
    status += f"Time: {datetime.now().strftime('%H:%M:%S')}"
    
    return status

if __name__ == "__main__":
    print(get_system_status())
