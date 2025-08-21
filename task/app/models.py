# app/models.py
from typing import List, Optional
from pydantic import BaseModel

# Stage 2/3
class InventoryResponse(BaseModel):
    usable_items: List[str]
    message: Optional[str] = None

class DietResponse(BaseModel):  # ok even if DietAgent returns dict
    compatible_items: List[str]
    suggested_recipe_ideas: List[str]

# Stage 4
class RecipeStep(BaseModel):
    step_number: int
    instruction: str

class RecipeResponse(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[RecipeStep]

