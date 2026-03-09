import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import DesignerAgent

app = create_agent_app(
    agent_class=DesignerAgent,
    service_name="designer",
    default_port=8007,
    telegram_token_env="DESIGNER_TOKEN"  # если будет Telegram-бот
)