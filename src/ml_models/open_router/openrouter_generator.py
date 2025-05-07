from src.ml_models.base_generator import BaseGenerator
from src.ml_models.open_router.utils import (
    send_chat_completion,
    send_chat_with_fallbacks,
    send_chat_with_any_route,
)

class OpenRouterGenerator(BaseGenerator):
    def send_message(self, prompt_text: str = None, **kwargs):
        state = self.get_prompt_state()
        prompt = prompt_text or state["prompt"]
        messages = [{"role": "user", "content": prompt}]
        model = self.config.get("model", "openai/gpt-3.5-turbo")
        fallbacks = self.config.get("fallbacks", [])
        route = self.config.get("route", None)
        if route == "any":
            models = self.config.get("models", [model] + fallbacks)
            return send_chat_with_any_route(models, messages, **kwargs)
        elif fallbacks:
            return send_chat_with_fallbacks(model, messages, fallbacks, **kwargs)
        else:
            return send_chat_completion(model, messages, **kwargs)
