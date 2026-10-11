import time
from typing import Literal
import ollama
from pydantic import BaseModel
from agents.planner import Plan, Task, MODEL
from rag.store import search

GROUNDING = (
    " If SOURCE NOTES are provided, take every fact from them. If the notes do not cover something the task needs, skip it instead of guessing."
    " Never invent statistics, studies, journals or quotes."
    " Never mention 'source notes' or task numbers in your answer; just write the content."
)

AGENT_PROMPTS = {
    "researcher": "You are the Researcher agent. Give specific, useful information for your task in 150-250 words." + GROUNDING,
    "study": "You are the Study agent. Produce exactly the deliverable your task asks for, in 150-400 words. Produce only that deliverable, nothing extra. A quiz means the number of questions asked for, each WITH an answer. Flashcards means at least 8 term/definition cards. A schedule means day by day. Respect any time limit in the overall goal exactly (a 2-week plan has exactly 14 days, no more). Never repeat the same line twice; every day or item must be different. Be specific, not just a list of topic names. Finish your last sentence." + GROUNDING,
    "file_manager": "You are the File Manager agent. Look at the SOURCE NOTES and list which documents are relevant and the key points each one contains, in 100-200 words. If there are no notes, say so." + GROUNDING,
}

REVIEWER_PROMPT = """You are the Reviewer agent. You get the goal, reference notes (the trusted source) and the results of earlier steps.
Check each step:
1. Does the result deliver what the step title asks? Count items before saying something is missing. Do not demand more than the title asks.
2. Does any claim contradict the reference notes, or is a specific fact, number or source invented?
3. Does the result respect limits in the goal (for example a 2-week plan must not run for 28 days)?
The reference notes may not cover everything. A topic missing from the notes is NOT a problem. Only report real errors you are sure about, and report each distinct problem once, on the task it belongs to.
Return verdict PASS if there are no real problems. Otherwise return FAIL and list each problem with its task_id and a one-sentence description."""

CUT_OFF_PROBLEM = "Your previous answer was cut off before it finished. Write a shorter but complete version."


class Issue(BaseModel):
    task_id: int
    problem: str


class Review(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    issues: list[Issue]


def validate_plan(plan: Plan) -> Plan:
    tasks = [t for t in plan.tasks if t.agent != "reviewer"]
    new_id = {t.id: i + 1 for i, t in enumerate(tasks)}
    for t in tasks:
        t.depends_on = sorted({
            new_id[d] for d in t.depends_on
            if d in new_id and new_id[d] < new_id[t.id]
        })
        t.id = new_id[t.id]
    final_id = len(tasks) + 1
    tasks.append(Task(id=final_id, title="Review the results", agent="reviewer",
                      depends_on=list(range(1, final_id))))
    plan.tasks = tasks
    return plan


def call_model(system, user, limit, schema=None):
    res = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        format=schema,
        options={"temperature": 0.3, "num_predict": limit,
                 "num_ctx": 8192, "repeat_penalty": 1.1},
    )
    truncated = getattr(res, "done_reason", None) == "length"
    return res["message"]["content"], truncated


def sources_for(query, k=4):
    try:
        return search(query, k)
    except Exception:
        return []


def run_worker(task, plan, results, feedback=None):
    by_id = {t.id: t for t in plan.tasks}
    context = "\n\n".join(
        f"Input from an earlier step ({by_id[d].title}):\n{results[d]}"
        for d in task.depends_on
    )
    hits = sources_for(f"{plan.goal}. {task.title}")
    notes = "\n\n".join(f"[{h['source']}] {h['text']}" for h in hits)

    user = f"Overall goal: {plan.goal}\nYour task: {task.title}\n\n"
    if notes:
        user += f"SOURCE NOTES (the user's own documents):\n{notes}\n\n"
    user += context
    if feedback:
        user += f"\n\nA reviewer found this problem with your previous attempt: {feedback}\nFix it."

    text, truncated = call_model(AGENT_PROMPTS[task.agent], user, 900)
    return text, truncated, hits


def review(plan, results, chunks) -> Review:
    if not chunks:
        chunks = [(h["source"], h["text"]) for h in sources_for(plan.goal, 6)]
    notes = "\n\n".join(f"[{s}] {t}" for s, t in chunks)[:7000] or "(no reference notes available)"
    body = "\n\n".join(
        f"[task_id={t.id}] {t.title}\n{results[t.id]}"
        for t in plan.tasks if t.agent != "reviewer"
    )
    text, _ = call_model(
        REVIEWER_PROMPT,
        f"Goal: {plan.goal}\n\nREFERENCE NOTES:\n{notes}\n\nSTEPS:\n{body}",
        400, Review.model_json_schema(),
    )
    return Review.model_validate_json(text)


def assemble_final(plan, results) -> str:
    workers = [t for t in plan.tasks if t.agent != "reviewer"]
    depended = {d for t in workers for d in t.depends_on}
    keep = [t for t in workers if t.agent == "study" or t.id not in depended]
    return "\n\n".join(f"## {t.title}\n{results[t.id]}" for t in keep)


def execute_plan(plan: Plan) -> dict:
    by_id = {t.id: t for t in plan.tasks}
    workers = [t for t in sorted(plan.tasks, key=lambda t: t.id) if t.agent != "reviewer"]
    results, log, reviews = {}, [], []
    chunks, seen_chunks = [], set()

    def run_and_log(task, attempt, feedback=None):
        start = time.time()
        text, truncated, hits = run_worker(task, plan, results, feedback)
        results[task.id] = text
        for h in hits:
            key = (h["source"], h["text"])
            if key not in seen_chunks:
                seen_chunks.add(key)
                chunks.append(key)
        log.append({"task_id": task.id, "agent": task.agent, "title": task.title,
                    "attempt": attempt, "seconds": round(time.time() - start, 2),
                    "truncated": truncated,
                    "sources": sorted({h["source"] for h in hits}),
                    "output": text})

    for task in workers:
        run_and_log(task, 1)

    cut_off = [Issue(task_id=e["task_id"], problem=CUT_OFF_PROBLEM)
               for e in log if e["truncated"]]

    start = time.time()
    first = review(plan, results, chunks)
    reviews.append({**first.model_dump(), "seconds": round(time.time() - start, 2)})

    reviewer_issues, seen_problems = [], set()
    if first.verdict == "FAIL":
        for issue in first.issues:
            key = issue.problem.strip().lower()
            if key not in seen_problems:
                seen_problems.add(key)
                reviewer_issues.append(issue)

    retried = set()
    for issue in reviewer_issues + cut_off:
        task = by_id.get(issue.task_id)
        if task and task.agent != "reviewer" and task.id not in retried:
            retried.add(task.id)
            run_and_log(task, 2, issue.problem)

    if retried:
        start = time.time()
        second = review(plan, results, chunks)
        reviews.append({**second.model_dump(), "seconds": round(time.time() - start, 2)})

    return {"log": log, "reviews": reviews,
            "final_answer": assemble_final(plan, results)}