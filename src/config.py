import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Assistant Settings
    ASSISTANT_NAME: str = "DEXTER"
    PERSONALITY: str = "You are DEXTER, a highly advanced local AI assistant. You are polite, efficient, and slightly witty, similar to JARVIS from Iron Man. Your goal is to assist the user with their tasks locally and securely."
    
    # Model Settings (Ollama)
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # STT Settings (Whisper)
    WHISPER_MODEL: str = "base"  # options: tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"  # set to "cuda" if GPU is available
    
    # TTS Settings
    TTS_VOICE_INDEX: int = 0  # Index of the voice to use in pyttsx3
    TTS_RATE: int = 200      # Speed of speech
    
    # Path Settings
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEMORY_DB_PATH: str = os.path.join(BASE_DIR, "dexter_memory.db")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
