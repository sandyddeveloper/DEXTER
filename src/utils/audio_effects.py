import winsound
import time
import logging

logger = logging.getLogger(__name__)

def play_jarvis_beep():
    """
    Plays a futuristic double-beep sound using Windows system sounds.
    """
    try:
        # Futuristic JARVIS-like pattern (High frequency, short duration)
        winsound.Beep(1000, 100) # 1000Hz for 100ms
        time.sleep(0.05)
        winsound.Beep(1500, 150) # 1500Hz for 150ms
    except Exception as e:
        logger.error(f"Failed to play beep: {e}")

if __name__ == "__main__":
    play_jarvis_beep()
