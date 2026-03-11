import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Корневая папка проектов ai-agents
    AGENTS_ROOT = Path(os.getenv("AGENTS_ROOT", Path.home() / "ai-agents" / "services"))
    # Файл с информацией об агентах (можно загружать из архитектора или держать локально)
    AGENTS_CONFIG = AGENTS_ROOT.parent / "config" / "agents_registry.yaml"