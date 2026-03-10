import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="API Gateway for AI Agents")

# Настройка CORS для Vue (порт 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация агентов (порты)
AGENTS = {
    "designer": "http://localhost:8007",
    "mentor": "http://localhost:8006",
    "secretary": "http://localhost:8002",
    "family": "http://localhost:8003",
    "architect": "http://localhost:8005",
    "english_mentor": "http://localhost:8004",
}

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "web_user"
    chat_id: Optional[str] = "web"

@app.post("/chat/{agent_name}")
async def chat_with_agent(agent_name: str, request: ChatRequest):
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_url = f"{AGENTS[agent_name]}/chat"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                agent_url,
                json={
                    "message": request.message,
                    "user_id": request.user_id,
                    "chat_id": request.chat_id
                },
                timeout=60.0
            )
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Agent timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agents": list(AGENTS.keys())}