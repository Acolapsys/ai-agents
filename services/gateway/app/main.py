import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Настройка логирования
log_dir = Path.home() / "ai-agents" / "logs" / "gateway"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "service.log"

# Создаём логгер
logger = logging.getLogger("gateway")
logger.setLevel(logging.INFO)

# Хендлер для файла с ротацией
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Также выводим в консоль (опционально)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

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
            logger.warning(f"Timeout for agent {agent_name}")
            raise HTTPException(status_code=504, detail="Agent timeout")
        except Exception as e:
            logger.error(f"Error calling agent {agent_name}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agents": list(AGENTS.keys())}

@app.get("/history/{agent_name}")
async def get_agent_history(agent_name: str, chat_id: str, limit: int = 50):
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_url = f"{AGENTS[agent_name]}/history"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(agent_url, params={"chat_id": chat_id, "limit": limit}, timeout=30.0)
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching history for {agent_name}: {e}")
            return []