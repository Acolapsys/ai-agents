import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import EnglishMentorAgent

app = create_agent_app(
    agent_class=EnglishMentorAgent,
    service_name="english_mentor",
    default_port=8004,
    telegram_token_env="ENGLISH_MENTOR_TOKEN"
)