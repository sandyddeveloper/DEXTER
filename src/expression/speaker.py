import edge_tts
import asyncio
import pygame
import threading
import os
import logging
from src.config import settings

logger = logging.getLogger(__name__)

class Speaker:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            # Jarvis-like voice: Ryan (UK) or Christopher (US)
            self.voice = "en-GB-RyanNeural"
            self.temp_file = "speech_output.mp3"
            
            # Fallback local engine (pyttsx3)
            import pyttsx3
            self.fallback_engine = pyttsx3.init()
            # Find a male voice if possible
            voices = self.fallback_engine.getProperty('voices')
            for v in voices:
                if "male" in v.name.lower():
                    self.fallback_engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            logger.error(f"Failed to initialize Speaker: {e}")

    async def _amplify_and_play(self, text: str):
        """Asynchronously generates and plays speech with offline fallback."""
        try:
            # Try Premium Voice (requires internet)
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://google.com", timeout=2) as resp:
                    if resp.status == 200:
                        communicate = edge_tts.Communicate(text, self.voice)
                        await communicate.save(self.temp_file)
                        
                        pygame.mixer.music.load(self.temp_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                        pygame.mixer.music.unload()
                        return

        except Exception as e:
            logger.warning(f"Premium TTS unavailable, falling back to local: {e}")
            
        # Local Fallback (Offline)
        try:
            self.fallback_engine.say(text)
            self.fallback_engine.runAndWait()
        except Exception as fallback_err:
            logger.error(f"Final TTS Failure: {fallback_err}")
            print(f"[DEXTER]: {text}")

    def speak(self, text: str):
        """Thread-safe entry point for speaking."""
        # Run the async playback in a new thread with its own event loop
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._amplify_and_play(text))
            loop.close()

        threading.Thread(target=run_async, daemon=True).start()

# Singleton instance
speaker = Speaker()
