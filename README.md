# DEXTER: Project-JARVIS (Local Edition)

DEXTER is a top-tier assistant built for privacy, performance, and total offline control. Inspired by Iron Man's JARVIS, it runs entirely on your local machine with no external API calls or tracking.

## 🚀 Features
- **Total Privacy**: 100% local processing (No Cloud, No APIs).
- **Intelligence**: Driven by **Ollama (Llama 3)**.
- **Voice Recognition**: High-speed offline transcription via **Faster-Whisper**.
- **Neural TTS**: Natural-sounding offline voice using **pyttsx3**.
- **System Integration**: Built-in Windows automation (Open apps, system control).
- **Auto-Start**: Systems wake up automatically on laptop boot.

## 🛠 Setup
1. **Prerequisites**:
   - Install [Ollama](https://ollama.com/) and run `ollama pull llama3`.
   - Python 3.10+.
2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Register Auto-Start**:
   ```bash
   python -m scripts.setup_autostart
   ```

## 🎮 Usage
Run the main orchestrator:
```bash
python -m src.main
```

## 📂 Architecture
- `src/core/brain.py`: LLM logic and personality.
- `src/perception/listener.py`: Local speech-to-text.
- `src/expression/speaker.py`: Text-to-speech.
- `src/expression/ui.py`: Futuristic terminal interface.
- `src/skills/`: Custom modules for system control.

## 🔒 Security
DEXTER does not require an internet connection. All data stays in `dexter_memory.db`.