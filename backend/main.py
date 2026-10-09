from fastapi import FastAPI
from pydantic import BaseModel
from agents.planner import create_plan, Plan
from orchestrator.engine import validate_plan, execute_plan
import ollama

app = FastAPI(title="NEXORA LifeOS")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    res = ollama.chat(
        model="qwen2.5:3b",
        messages=[{"role": "user", "content": req.message}],
    )
    return {"reply": res["message"]["content"]}

class PlanRequest(BaseModel):
    goal: str

@app.post("/plan", response_model=Plan)
def plan(req: PlanRequest):
    return create_plan(req.goal)

@app.post("/run")
def run(req: PlanRequest):
    plan = validate_plan(create_plan(req.goal))
    return {"plan": plan, "results": execute_plan(plan)}