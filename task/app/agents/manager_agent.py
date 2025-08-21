# agents/manager_agent.py
from typing import List, Dict, Any
from app.agents.inventory_agent import InventoryAgent
from app.agents.diet_agent import DietAgent

class ManagerAgent:
    def __init__(self):
        self.inventory_agent = InventoryAgent()
        self.diet_agent = DietAgent()

    def run(self, items: List[str], diet: str) -> Dict[str, Any]:
        # Inventory step
        inv_result = self.inventory_agent.run(items)
        usable_items = (
            inv_result.usable_items if hasattr(inv_result, "usable_items")
            else inv_result.get("usable_items", [])
        )

        # Diet filtering step
        diet_result = self.diet_agent.run(usable_items, diet)
        diet_filtered = diet_result.get("compatible_items", [])
        suggestions = diet_result.get("suggested_recipe_ideas", [])

        return {
            "usable_items": list(usable_items),
            "diet_filtered": list(diet_filtered),
            "suggestions": list(suggestions),
        }

