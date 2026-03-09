import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import FamilyAgent

app = create_agent_app(
    agent_class=FamilyAgent,
    service_name="family",
    default_port=8003,
    telegram_token_env="FAMILY_TOKEN"
)