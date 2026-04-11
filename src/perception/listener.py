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
        self.r.energy_threshold = 4000 # Default sensitivity
        self.r.dynamic_energy_threshold = True
        self.boot_model = settings.WHISPER_BOOT_MODEL
        self.main_model = settings.WHISPER_MAIN_MODEL
        self.device = settings.WHISPER_DEVICE
        self.model = None
        self.model_path = "LOADING..." # Initialize early for telemetry
        self.wake_word = settings.ASSISTANT_NAME.lower()

    def _initialize_model(self, model_size=None, local_files_only=False):
        """Asynchronously attempts to load the Whisper model."""
        target_model = model_size if model_size else self.boot_model
        if self.model is None or (model_size and self.model_path != model_size):
            try:
                logger.info(f"Loading Whisper model: {target_model} (Local Only: {local_files_only})")
                self.model = WhisperModel(target_model, device=self.device, compute_type="int8", local_files_only=local_files_only)
                self.model_path = target_model
                return True
            except Exception as e:
                logger.error(f"Failed to load Whisper model {target_model}: {e}")
                return False
        return True

    def upgrade_model(self, local_files_only=False):
        """Swaps the boot model for the high-accuracy main model."""
        if self.model_path != self.main_model:
            logger.info(f"Upgrading neural perception to high-accuracy core... (Local Only: {local_files_only})")
            self._initialize_model(self.main_model, local_files_only=local_files_only)

    @property
    def is_ready(self):
        return self.model is not None

    def listen_for_wake_word(self):
        """
        Optimized background listener.
        """
        try:
            with sr.Microphone() as source:
                # Fast noise adjustment
                self.r.adjust_for_ambient_noise(source, duration=0.3)
                
                # Shorter buffer for instant detection
                audio = self.r.listen(source, phrase_time_limit=2)
                
                with open("wake_temp.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                if not self._initialize_model():
                    return False
                
                # Use beam_size=1 for maximum speed on wake word
                segments, _ = self.model.transcribe("wake_temp.wav", beam_size=1)
                text = " ".join([segment.text for segment in segments]).lower()
                
                if self.wake_word in text:
                    logger.info("DEXTER Detected")
                    play_jarvis_beep()
                    return True
                    
                return False
        except Exception:
            return False
        finally:
            if os.path.exists("wake_temp.wav"):
                os.remove("wake_temp.wav")

    def listen_to_command(self):
        """
        High-accuracy command perception.
        """
        try:
            with sr.Microphone() as source:
                # Command listening should be more patient
                audio = self.r.listen(source, timeout=3, phrase_time_limit=8)
                
                with open("cmd_temp.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                if not self._initialize_model():
                    return None
                
                # Use beam_size=5 for accuracy on commands
                segments, _ = self.model.transcribe("cmd_temp.wav", beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip()
                
                return text
                
        except Exception as e:
            logger.error(f"Perception failure: {e}")
            return None
        finally:
            if os.path.exists("cmd_temp.wav"):
                os.remove("cmd_temp.wav")

listener = Listener()
