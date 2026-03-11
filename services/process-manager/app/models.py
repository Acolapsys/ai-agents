from pydantic import BaseModel
from typing import Optional

class AgentInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    run_script: str               # путь к run.sh относительно AGENTS_ROOT/agent_id
    status: str = "stopped"       # running, stopped, error
    pid: Optional[int] = None
    port: Optional[int] = None