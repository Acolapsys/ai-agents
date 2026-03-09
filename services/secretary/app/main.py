import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import SecretaryAgent

app = create_agent_app(
    agent_class=SecretaryAgent,
    service_name="secretary",
    default_port=8002,
    telegram_token_env="SECRETARY_TOKEN"
)