import asyncio
import sys
from src.core.brain import brain
from src.expression.ui import ui
from src.expression.speaker import speaker
from src.perception.listener import listener
from src.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_interaction(user_input):
    """Processes a single interaction."""
    # Process with Brain
    ui.show_status("Thinking")
    response = await brain.chat(user_input)

    # Express
    ui.print_assistant(response)
    speaker.speak(response)

async def main_loop():
    ui.show_welcome()
    
    # Initial greeting
    greeting = f"Systems initialized. {settings.ASSISTANT_NAME} is at your service, sir. Standing by."
    ui.print_assistant(greeting)
    speaker.speak(greeting)

    mode = "voice" # can be 'voice' or 'text'
    
    while True:
        try:
            if mode == "voice":
                ui.show_status("Standby (Waiting for 'DEXTER')")
                # Wait for wake word in the background
                if listener.listen_for_wake_word():
                    ui.show_status("Listening")
                    command = listener.listen_to_command()
                    
                    if command:
                        ui.print_user(command)
                        await run_interaction(command)
                
            else:
                # Text mode fallback
                ui.show_status("Text Mode Active")
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, ">> ")
                
                if user_input.lower() in ['voice', 'enable voice']:
                    mode = "voice"
                    continue
                
                if not user_input or user_input.lower() in ['exit', 'quit', 'shutdown']:
                    break
                    
                ui.print_user(user_input)
                await run_interaction(user_input)

        except KeyboardInterrupt:
            break
        except Exception as e:
            ui.print_error(f"Main Loop Error: {e}")
            # If voice fails drastically, fallback to text
            mode = "text"
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
