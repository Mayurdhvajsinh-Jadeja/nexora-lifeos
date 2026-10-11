from fastapi import FastAPI
from pydantic import BaseModel
import ollama

from agents.planner import create_plan, Plan
from orchestrator.engine import validate_plan, execute_plan
from rag.store import ingest_folder, search

app = FastAPI(title="NEXORA LifeOS")


class ChatRequest(BaseModel):
    message: str


class PlanRequest(BaseModel):
    goal: str


class SearchRequest(BaseModel):
    query: str
    k: int = 4


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


@app.post("/ingest")
def ingest():
    return {"ingested": ingest_folder()}


@app.post("/search")
def search_docs(req: SearchRequest):
    return {"results": search(req.query, req.k)}


@app.post("/plan", response_model=Plan)
def plan(req: PlanRequest):
    return create_plan(req.goal)


@app.post("/run")
def run(req: PlanRequest):
    plan = validate_plan(create_plan(req.goal))
    return {"plan": plan, **execute_plan(plan)}