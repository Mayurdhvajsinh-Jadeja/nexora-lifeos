import time
import ollama
from agents.planner import Plan, Task, MODEL

AGENT_PROMPTS = {
    "researcher": "You are the Researcher agent. Give accurate, concise information for the task.",
    "study": "You are the Study agent. Turn information into clear study material: notes, summaries, flashcards or schedules.",
    "file_manager": "You are the File Manager agent. Document search is not connected yet, so say what you would look for.",
    "reviewer": "You are the Reviewer agent. Check the earlier results for errors, gaps or irrelevance, then give a short, improved final answer.",
}

def validate_plan(plan: Plan) -> Plan:
    ids = {t.id for t in plan.tasks}
    # keep only dependencies that exist and come earlier
    for t in plan.tasks:
        t.depends_on = sorted({d for d in t.depends_on if d in ids and d < t.id})
    # the plan must end with a reviewer that depends on everything before it
    if plan.tasks[-1].agent != "reviewer":
        next_id = plan.tasks[-1].id + 1
        plan.tasks.append(Task(id=next_id, title="Review the final result",
                               agent="reviewer", depends_on=[]))
    last = plan.tasks[-1]
    last.depends_on = [t.id for t in plan.tasks if t.id < last.id]
    return plan

def run_task(task: Task, goal: str, results: dict) -> str:
    context = "\n\n".join(
        f"Result of task {d}:\n{results[d]}" for d in task.depends_on
    )
    res = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": AGENT_PROMPTS[task.agent]},
            {"role": "user", "content": f"Overall goal: {goal}\nYour task: {task.title}\n\n{context}"},
        ],
        options={"temperature": 0.3},
    )
    return res["message"]["content"]

def execute_plan(plan: Plan) -> list[dict]:
    results, log = {}, []
    for task in sorted(plan.tasks, key=lambda t: t.id):
        start = time.time()
        results[task.id] = run_task(task, plan.goal, results)
        log.append({
            "task_id": task.id,
            "agent": task.agent,
            "seconds": round(time.time() - start, 2),
            "output": results[task.id],
        })
    return log