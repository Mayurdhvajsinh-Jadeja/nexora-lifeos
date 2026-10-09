from fastapi import FastAPI
from pydantic import BaseModel
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