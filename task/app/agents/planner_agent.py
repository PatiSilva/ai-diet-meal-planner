# app/agents/planner_agent.py
from typing import List, Dict, Any
from app.services.llm_client import LLMClient
from app.models import RecipeResponse, RecipeStep


class PlannerAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, base_recipe: str) -> RecipeResponse:
        prompt = (
            "You are a recipe planner. Produce STRICT JSON matching this schema:\n"
            "{"
            '  "title": string,'
            '  "ingredients": [string, ...],'
            '  "steps": [ { "step_number": integer, "instruction": string }, ... ]'
            "}\n"
            "- 5–10 ingredients, plain strings.\n"
            "- 4–8 steps, imperative and concise.\n"
            "- Respond with VALID JSON ONLY. No preface, no code fences.\n"
            f'Base recipe: "{base_recipe}"'
        )
        try:
            raw = self.llm.call_model_json(prompt)  # dict or {}
        except Exception as e:
            print(f"⚠️ PlannerAgent LLM error: {e}")
            return self._fallback_recipe(base_recipe)

        if not isinstance(raw, dict) or not raw:
            return self._fallback_recipe(base_recipe)

        try:
            result = self._normalize(raw)
        except Exception as e:
            print(f"⚠️ PlannerAgent normalize error: {e}")
            return self._fallback_recipe(base_recipe)

        # Ensure non-empty fields
        if not result.title or not result.ingredients or not result.steps:
            return self._fallback_recipe(base_recipe)

        return result

    def _normalize(self, obj: Dict[str, Any]) -> RecipeResponse:
        title = (obj.get("title") or "").strip()

        # ingredients: list[str] OR string (comma/newline separated)
        ing_raw = obj.get("ingredients", [])
        ingredients: List[str] = []
        if isinstance(ing_raw, list):
            ingredients = [str(x).strip() for x in ing_raw if str(x).strip()]
        else:
            s = str(ing_raw)
            parts = [p.strip() for p in s.split(",")]
            if len(parts) <= 1:
                parts = [p.strip() for p in s.splitlines()]
            ingredients = [p for p in parts if p]

        # steps: list[dict] OR list[str] OR string
        steps_raw = obj.get("steps", [])
        steps: List[RecipeStep] = []
        if isinstance(steps_raw, list):
            if steps_raw and isinstance(steps_raw[0], dict):
                for s in steps_raw:
                    instr = str(s.get("instruction", "")).strip()
                    num = s.get("step_number")
                    try:
                        num = int(num) if num is not None else None
                    except Exception:
                        num = None
                    if instr:
                        steps.append(RecipeStep(step_number=num or (len(steps) + 1), instruction=instr))
            else:
                for i, s in enumerate(steps_raw, start=1):
                    instr = str(s).strip()
                    if instr:
                        steps.append(RecipeStep(step_number=i, instruction=instr))
        else:
            txt = str(steps_raw).strip()
            if txt:
                steps.append(RecipeStep(step_number=1, instruction=txt))

        # normalize numbering 1..n
        steps = [RecipeStep(step_number=i, instruction=st.instruction) for i, st in enumerate(steps, start=1)]

        return RecipeResponse(
            title=title or "Simple Recipe",
            ingredients=ingredients,
            steps=steps,
        )

    def _fallback_recipe(self, base_recipe: str) -> RecipeResponse:
        title = (base_recipe or "Simple Recipe").strip()
        ingredients = ["oil", "salt", "pepper", "garlic", "onion"]
        steps = [
            RecipeStep(step_number=1, instruction="Prep ingredients."),
            RecipeStep(step_number=2, instruction="Heat oil in pan."),
            RecipeStep(step_number=3, instruction="Cook and season."),
            RecipeStep(step_number=4, instruction="Serve warm."),
        ]
        return RecipeResponse(title=title, ingredients=ingredients, steps=steps)

