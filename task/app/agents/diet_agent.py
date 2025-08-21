from app.services.llm_client import LLMClient
from app.models import DietResponse


class DietAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, items: list, diet: str) -> dict:
        prompt = (
            f"You are a diet assistant. Given this list of ingredients: {items}, and the diet type: '{diet}',\n"
            "return a JSON object with:\n"
            "- compatible_items: ingredients that fit the diet,\n"
            "- suggested_recipe_ideas: a list of 5 recipe names based on the compatible items.\n"
            "Respond ONLY with valid JSON."
        )

        result = self.llm.call_model_json(prompt)
        return result  # No json.loads()!


