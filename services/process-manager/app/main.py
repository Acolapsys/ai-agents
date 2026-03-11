from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .manager import ProcessManager
from .models import AgentInfo

app = FastAPI(title="Process Manager API")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # адрес Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ProcessManager()

@app.get("/agents", response_model=dict[str, AgentInfo])
async def list_agents():
    """Возвращает всех агентов с актуальными статусами"""
    return manager.list_agents()

@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    agents = manager.list_agents()
    if agent_id not in agents:
        raise HTTPException(404, "Agent not found")
    return agents[agent_id]

@app.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    if manager.start_agent(agent_id):
        return {"status": "started"}
    raise HTTPException(500, "Failed to start agent")

@app.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    if manager.stop_agent(agent_id):
        return {"status": "stopped"}
    raise HTTPException(500, "Failed to stop agent")

@app.post("/agents/{agent_id}/restart")
async def restart_agent(agent_id: str):
    if manager.restart_agent(agent_id):
        return {"status": "restarted"}
    raise HTTPException(500, "Failed to restart agent")

@app.get("/agents/{agent_id}/logs")
async def get_agent_logs(agent_id: str, limit: int = 50, offset: int = 0):
    result = manager.read_agent_log(agent_id, limit, offset)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Log not found"))
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/agents/start-all")
async def start_all_agents():
    results = {}
    for agent_id in manager.agents:
        results[agent_id] = manager.start_agent(agent_id)
    return results

@app.post("/agents/stop-all")
async def stop_all_agents():
    results = {}
    for agent_id in manager.agents:
        results[agent_id] = manager.stop_agent(agent_id)
    return results