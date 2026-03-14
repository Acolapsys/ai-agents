import os
import logging
import yaml
import asyncio
from logging.handlers import RotatingFileHandler
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict

from dotenv import load_dotenv


# Настройка логирования
log_dir = Path.home() / "ai-agents" / "logs" / "gateway"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "service.log"

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

# Загружаем общий .env
root_env = Path(__file__).parent.parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
    logger.info(f"Loaded root env from {root_env}")

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
AGENTS_CONFIG = {
    "designer": "http://localhost:8007",
    "mentor": "http://localhost:8006",
    "secretary": "http://localhost:8002",
    "family": "http://localhost:8003",
    "architect": "http://localhost:8005",
    "english_mentor": "http://localhost:8004",
}

# Загружаем конфигурацию агентов из YAML
def load_agents_config() -> Dict[str, str]:
    """Загружает список агентов из agents_registry.yaml и возвращает словарь {agent_id: base_url}."""
    config_path = Path.home() / "ai-agents" / "config" / "agents_registry.yaml"
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        # Fallback для разработки (хардкод)
        logger.warning("Using hardcoded fallback configuration")
        return AGENTS_CONFIG
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            agents = {}
            for agent_id, info in data.get('agents', {}).items():
                port = info.get('port')
                if port:
                    agents[agent_id] = f"http://localhost:{port}"
                else:
                    logger.warning(f"Agent {agent_id} has no port defined, skipping")
            if not agents:
                logger.error("No agents with valid port found in config")
                return {}
            logger.info(f"Loaded {len(agents)} agents from config: {list(agents.keys())}")
            return agents
    except Exception as e:
        logger.error(f"Failed to load agents config: {e}")
        return {}

# Инициализируем конфигурацию
AGENTS = load_agents_config()

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
    return {"status": "ok"}

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

@app.get("/dashboard")
async def get_dashboard():
    async with httpx.AsyncClient() as client:
        # Параллельно опрашиваем
        tasks = [
            client.get("http://localhost:8008/agents"),
            client.get("http://localhost:8009/tasks"),
            client.get("http://localhost:8009/logs/last?lines=50"),
            client.get("http://localhost:8008/health"),
            client.get("http://localhost:8000/health"),
            client.get("http://localhost:8009/health"),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Функция для безопасного получения JSON
        def safe_json(resp, default=None):
            if isinstance(resp, httpx.Response) and resp.status_code == 200:
                try:
                    return resp.json()
                except:
                    pass
            return default if default is not None else {}

        agents_data = safe_json(results[0], {})
        tasks_data = safe_json(results[1], [])
        logs_data = safe_json(results[2], {"logs": []})
        pm_health = safe_json(results[3], {"status": "error"})
        gw_health = safe_json(results[4], {"status": "error"})
        tm_health = safe_json(results[5], {"status": "error"})

        # Преобразуем агентов в массив
        agents_list = []
        if agents_data:
            for aid, info in agents_data.items():
                info["id"] = aid
                agents_list.append(info)

        # Извлекаем важные события из логов
        important_events = []
        if logs_data and "logs" in logs_data:
            for line in logs_data["logs"]:
                if "ERROR" in line or "WARNING" in line:
                    important_events.append(line)

        return {
            "gateway": gw_health,
            "processManager": pm_health,
            "taskManager": tm_health,
            "agents": agents_list,
            "tasks": tasks_data,
            "importantEvents": important_events[:10]
        }

@app.get("/agents")
async def get_agents():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8008/agents", timeout=10.0)
            data = resp.json()
            # process-manager возвращает объект { agent_id: {...} }, преобразуем в массив
            agents_list = []
            for aid, info in data.items():
                info["id"] = aid
                agents_list.append(info)
            return agents_list
        except Exception as e:
            logger.error(f"Error fetching agents from process-manager: {e}")
            raise HTTPException(status_code=503, detail="Process Manager unavailable")