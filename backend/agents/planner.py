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
Break the user's goal into 3 to 5 small, concrete tasks that a text-only AI can complete by writing text.
Every task must directly serve the goal. Do not plan videos, meetings, group activities or anything that needs people or tools.
Each task must produce something NEW and different from the others. Never create two tasks that restate the same thing.
Write every task title as a short, normal English sentence with spaces, never with underscores. It must name its deliverable, for example "Write a 5-question quiz with answers on normalization" or "Make a day-by-day 14-day study schedule".
Keep any time limit from the goal in the titles (for example "14-day").
If the goal is about studying or working from the user's own material, start with a file_manager task that finds the relevant notes.
Each task needs: id (starting at 1), title, agent, depends_on (list of earlier task ids).
Agents: researcher (explains information), study (makes study material: notes, quizzes, flashcards, schedules),
file_manager (searches the user's documents).
Do not create a reviewer task; it is added automatically.
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