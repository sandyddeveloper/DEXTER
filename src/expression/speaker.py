import pyttsx3
import threading
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class Speaker:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', settings.TTS_RATE)
            self.engine.setProperty('volume', 1.0)
            
            # Select voice
            voices = self.engine.getProperty('voices')
            if len(voices) > settings.TTS_VOICE_INDEX:
                self.engine.setProperty('voice', voices[settings.TTS_VOICE_INDEX].id)
            
            self._lock = threading.Lock()
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.engine = None

    def speak(self, text: str):
        """
        Speak text in a thread-safe manner.
        """
        if not self.engine:
            return
            
        def _say():
            with self._lock:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    logger.error(f"Error in TTS execution: {e}")

        # Running in a thread to prevent blocking the async loop
        threading.Thread(target=_say, daemon=True).start()

# Singleton instance
speaker = Speaker()
