import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

from agents.planner import create_plan, Plan
from orchestrator.engine import validate_plan, execute_plan
from rag.store import ingest_folder, search
from db.runlog import save_run, list_runs, get_run, agent_stats

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
    start = time.time()
    plan = validate_plan(create_plan(req.goal))
    result = execute_plan(plan)
    run_id = save_run(plan, result, time.time() - start)
    return {"run_id": run_id, "plan": plan, **result}


@app.get("/runs")
def runs(limit: int = 20):
    return {"runs": list_runs(limit)}


@app.get("/runs/{run_id}")
def run_detail(run_id: int):
    data = get_run(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return data


@app.get("/stats")
def stats():
    return {"agents": agent_stats()}