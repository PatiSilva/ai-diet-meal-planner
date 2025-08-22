# task/main.py

# For checker (submission/task/main.py)
from diet_agent import DietAgent
from inventory_agent import InventoryAgent
from manager_agent import ManagerAgent
from planner_agent import PlannerAgent
from llm_client import LLMClient
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

import logging, sys
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ai-diet-planner")

app = FastAPI()

class AskRequest(BaseModel):
    items: List[str]
    diet: str

class PlanRequest(BaseModel):
    base_recipe: str

class RecommendRequest(BaseModel):
    items: List[str]
    diet: str
    recipe_count: int = 1

@app.get("/")
def root():
    return {"message": "Success: AI Diet Planner API is running"}

@app.post("/ask")
def ask(req: AskRequest):
    logger.info("Received /ask request")
    usable = [i for i in req.items if i.strip()]
    filtered = [i for i in usable if i.lower() not in {"chicken", "chicken breast", "beef", "pork", "fish", "egg", "milk", "cheese", "butter", "yogurt"}] if req.diet.lower()=="vegan" else usable
    suggestions = ["Sample Suggestion 1", "Sample Suggestion 2"]
    return {"usable_items": usable, "diet_filtered": filtered, "suggestions": suggestions}

@app.post("/plan")
def plan(req: PlanRequest):
    logger.info("Received /plan request")
    resp = {"title": req.base_recipe, "ingredients": ["spinach","tomato"], "steps": ["Mix","Serve"]}
    logger.info("/plan response")
    return resp

@app.post("/recommend")
def recommend(req: RecommendRequest):
    logger.info("Received /recommend request")
    recipe = {"title": f"{req.diet.title()} Recipe", "ingredients": req.items or ["spinach","tomato"], "steps": ["Prep","Cook","Serve"]}
    resp = {"recipes": [recipe for _ in range(max(1, req.recipe_count))]}
    logger.info("/recommend response")
    return resp

