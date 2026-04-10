import speech_recognition as sr
from faster_whisper import WhisperModel
from src.config import settings
from src.utils.audio_effects import play_jarvis_beep
import logging
import os
import time

logger = logging.getLogger(__name__)

class Listener:
    def __init__(self):
        self.r = sr.Recognizer()
        self.model_path = settings.WHISPER_MODEL
        self.device = settings.WHISPER_DEVICE
        self.model = None
        self.wake_word = settings.ASSISTANT_NAME.lower()

    def _initialize_model(self):
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_path}")
            self.model = WhisperModel(self.model_path, device=self.device, compute_type="int8")

    def listen_for_wake_word(self):
        """
        Background listener that waits for the keyword 'DEXTER'.
        """
        try:
            with sr.Microphone() as source:
                self.r.adjust_for_ambient_noise(source, duration=0.5)
                # logger.info("Background scanning for wake word...")
                
                # Listen for a short burst
                audio = self.r.listen(source, phrase_time_limit=3)
                
                with open("wake_temp.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                self._initialize_model()
                segments, _ = self.model.transcribe("wake_temp.wav", beam_size=1)
                text = " ".join([segment.text for segment in segments]).lower()
                
                if self.wake_word in text:
                    logger.info("Wake word DETECTED!")
                    play_jarvis_beep()
                    return True
                    
                return False
        except Exception as e:
            # logger.error(f"Wake word error: {e}")
            return False
        finally:
            if os.path.exists("wake_temp.wav"):
                os.remove("wake_temp.wav")

    def listen_to_command(self):
        """
        Listens to the actual command after DEXTER is awake.
        """
        try:
            with sr.Microphone() as source:
                # No need to adjust noise again, assume it's done
                logger.info("Listening for command...")
                audio = self.r.listen(source, timeout=5, phrase_time_limit=10)
                
                with open("cmd_temp.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                self._initialize_model()
                segments, _ = self.model.transcribe("cmd_temp.wav", beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip()
                
                return text
                
        except Exception as e:
            logger.error(f"Command perception error: {e}")
            return None
        finally:
            if os.path.exists("cmd_temp.wav"):
                os.remove("cmd_temp.wav")

# Singleton instance
listener = Listener()
