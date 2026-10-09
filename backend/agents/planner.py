from typing import Literal
import ollama
from pydantic import BaseModel

MODEL = "qwen2.5:3b"

class Task(BaseModel):
    id: int
    title: str
    agent: Literal["researcher", "study", "file_manager", "reviewer"]
    depends_on: list[int]

class PlanDraft(BaseModel):
    tasks: list[Task]

class Plan(BaseModel):
    goal: str
    tasks: list[Task]

SYSTEM_PROMPT = """You are the Planner agent of NEXORA LifeOS.
Break the user's goal into 3 to 6 small, concrete tasks.
Each task needs: id (starting at 1), title, agent, depends_on (list of earlier task ids).
Agents: researcher (finds information), study (explains and makes study material),
file_manager (searches the user's documents), reviewer (checks the final result).
The last task must always be done by the reviewer and depend on the other tasks.
Only depend on tasks with a smaller id."""

def create_plan(goal: str) -> Plan:
    res = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": goal},
        ],
        format=PlanDraft.model_json_schema(),
        options={"temperature": 0.2},
    )
    draft = PlanDraft.model_validate_json(res["message"]["content"])
    return Plan(goal=goal, tasks=draft.tasks)