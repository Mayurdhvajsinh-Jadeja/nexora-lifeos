import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "nexora.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    goal = Column(String)
    total_seconds = Column(Float)
    first_verdict = Column(String)
    final_verdict = Column(String)
    retries = Column(Integer)
    truncated_count = Column(Integer)
    plan_json = Column(Text)
    reviews_json = Column(Text)
    final_answer = Column(Text)


class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    task_id = Column(Integer)
    agent = Column(String)
    title = Column(String)
    attempt = Column(Integer)
    seconds = Column(Float)
    truncated = Column(Boolean)
    sources = Column(Text)
    output = Column(Text)


Base.metadata.create_all(engine)


def save_run(plan, result: dict, total_seconds: float) -> int:
    log = result["log"]
    reviews = result["reviews"]
    with SessionLocal() as s:
        run = Run(
            goal=plan.goal,
            total_seconds=round(total_seconds, 2),
            first_verdict=reviews[0]["verdict"] if reviews else None,
            final_verdict=reviews[-1]["verdict"] if reviews else None,
            retries=sum(1 for e in log if e["attempt"] > 1),
            truncated_count=sum(1 for e in log if e["truncated"]),
            plan_json=plan.model_dump_json(),
            reviews_json=json.dumps(reviews),
            final_answer=result["final_answer"],
        )
        s.add(run)
        s.flush()
        for e in log:
            s.add(TaskLog(
                run_id=run.id, task_id=e["task_id"], agent=e["agent"],
                title=e["title"], attempt=e["attempt"], seconds=e["seconds"],
                truncated=e["truncated"], sources=json.dumps(e["sources"]),
                output=e["output"],
            ))
        s.commit()
        return run.id


def list_runs(limit: int = 20) -> list[dict]:
    with SessionLocal() as s:
        runs = s.query(Run).order_by(Run.id.desc()).limit(limit).all()
        return [{
            "id": r.id, "created_at": r.created_at.isoformat(), "goal": r.goal,
            "total_seconds": r.total_seconds, "first_verdict": r.first_verdict,
            "final_verdict": r.final_verdict, "retries": r.retries,
            "truncated_count": r.truncated_count,
        } for r in runs]


def get_run(run_id: int):
    with SessionLocal() as s:
        r = s.get(Run, run_id)
        if r is None:
            return None
        tasks = s.query(TaskLog).filter(TaskLog.run_id == run_id).order_by(TaskLog.id).all()
        return {
            "id": r.id, "created_at": r.created_at.isoformat(), "goal": r.goal,
            "total_seconds": r.total_seconds, "first_verdict": r.first_verdict,
            "final_verdict": r.final_verdict, "retries": r.retries,
            "truncated_count": r.truncated_count,
            "plan": json.loads(r.plan_json), "reviews": json.loads(r.reviews_json),
            "final_answer": r.final_answer,
            "tasks": [{
                "task_id": t.task_id, "agent": t.agent, "title": t.title,
                "attempt": t.attempt, "seconds": t.seconds, "truncated": t.truncated,
                "sources": json.loads(t.sources), "output": t.output,
            } for t in tasks],
        }


def agent_stats() -> dict:
    with SessionLocal() as s:
        rows = s.query(TaskLog).all()
    stats = {}
    for r in rows:
        a = stats.setdefault(r.agent, {"first": 0, "retried": 0, "seconds": 0.0, "truncated": 0})
        if r.attempt == 1:
            a["first"] += 1
        else:
            a["retried"] += 1
        a["seconds"] += r.seconds
        if r.truncated:
            a["truncated"] += 1
    out = {}
    for agent, a in stats.items():
        calls = a["first"] + a["retried"]
        out[agent] = {
            "first_attempts": a["first"],
            "retry_rate": round(a["retried"] / (a["first"] or 1), 2),
            "avg_seconds_per_call": round(a["seconds"] / (calls or 1), 2),
            "truncated_calls": a["truncated"],
        }
    return out