import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import ArchitectAgent

app = create_agent_app(
    agent_class=ArchitectAgent,
    service_name="architect",
    default_port=8005,
    telegram_token_env="ARCHITECT_TOKEN"
)