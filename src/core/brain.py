import ollama
from src.config import settings
from src.skills.app_control import SKILLS as APP_SKILLS
import logging
import re

logger = logging.getLogger(__name__)

class Brain:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.history = []
        
        # Merge all skills
        self.skills = {**APP_SKILLS}
        
    def get_system_prompt(self):
        skills_desc = "\n".join([f"- {name}: {func.__doc__}" for name, func in self.skills.items()])
        
        return f"""{settings.PERSONALITY}

You have the ability to control the user's computer using the following skills:
{skills_desc}

If you need to use a skill, include the following format in your response: [[ACTION: skill_name]].
For example, if the user asks to open Chrome, you should say "Certainly, sir. Opening Chrome now. [[ACTION: open_chrome]]"

Respond naturally and professionally, like JARVIS.
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
            
            # Check for actions
            action_match = re.search(r"\[\[ACTION: (.*?)\]\]", assistant_response)
            action_result = None
            
            if action_match:
                skill_name = action_match.group(1).strip()
                if skill_name in self.skills:
                    logger.info(f"Executing skill: {skill_name}")
                    action_result = self.skills[skill_name]()
                    # Optionally append the result to the response or just let it happen
                    if action_result:
                        assistant_response = assistant_response.replace(action_match.group(0), f"\n(System: {action_result})")
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error in brain: {e}")
            return "I am experiencing localized cognitive interference. Please check my Ollama connection."

brain = Brain()
