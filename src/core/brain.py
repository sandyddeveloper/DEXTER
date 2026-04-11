import ollama
from src.config import settings
from src.skills.app_control import SKILLS as APP_SKILLS
from src.skills.system_control import SYSTEM_SKILLS
import logging
import re

logger = logging.getLogger(__name__)

class Brain:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.history = []
        
        # Merge all skills
        self.skills = {**APP_SKILLS, **SYSTEM_SKILLS}
        
    def get_system_prompt(self):
        skills_desc = "\n".join([f"- {name}: {func.__doc__}" for name, func in self.skills.items()])
        
        return f"""{settings.PERSONALITY}

You have control over the user's Windows system using these tools:
{skills_desc}

RULES:
1. To use a tool, output: [[ACTION: tool_name, argument]]
2. If argument is not needed, leave it empty: [[ACTION: tool_name]]
3. For 'lock_pc', you MUST ask for confirmation first unless the user explicitly said "DEXTER, I am leaving, lock the PC".

Examples:
- User: "Search for Iron Man" -> "Accessing web archives. [[ACTION: search_web, Iron Man]]"
- User: "Mute the audio" -> "Certainly, sir. Silencing systems. [[ACTION: set_volume, 0]]"
- User: "Set brightness to 80" -> "Adjusting displays. [[ACTION: set_brightness, 80]]"
- User: "Next song" -> "Skipping tracks. [[ACTION: control_media, next]]"
"""

    def add_to_history(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    async def chat(self, prompt: str):
        try:
            self.add_to_history("user", prompt)
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ] + self.history
            
            response = ollama.chat(
                model=self.model,
                messages=messages,
                stream=False
            )
            
            assistant_response = response['message']['content']
            self.add_to_history("assistant", assistant_response)
            
            # Action Parsing
            # Format: [[ACTION: name, arg]]
            action_match = re.search(r"\[\[ACTION: (.*?)(?:, (.*?))?\]\]", assistant_response)
            
            if action_match:
                skill_name = action_match.group(1).strip()
                arg = action_match.group(2).strip() if action_match.group(2) else None
                
                if skill_name in self.skills:
                    # Execute
                    if arg:
                        # Try to parse if it's an int for volume/brightness
                        try:
                            if skill_name in ['set_volume', 'set_brightness']:
                                arg = int(arg)
                        except: pass
                        result = self.skills[skill_name](arg)
                    else:
                        result = self.skills[skill_name]()
                        
                    if result:
                        assistant_response = assistant_response.replace(action_match.group(0), f"\n(Result: {result})")
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error in brain: {e}")
            return "Cognitive functions are slightly out of sync, sir. Please stand by."

brain = Brain()
