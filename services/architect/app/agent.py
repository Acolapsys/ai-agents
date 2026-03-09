import sys
from pathlib import Path
from datetime import datetime
import json
import yaml
import shutil
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "Виктор"

        # Путь к реестру агентов
        self.registry_path = self.agent_data_path / "registry" / "agents.yaml"
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    # --- Вспомогательные методы ---
    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {"agents": {}}

    def _save_registry(self):
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.registry, f, allow_unicode=True, sort_keys=False)

    def _get_agent_path(self, agent_id: str) -> Path:
        """Возвращает путь к папке сервиса агента."""
        return Path.home() / "ai-agents" / "services" / agent_id

    # --- Инструменты ---
    async def list_agents(self) -> str:
        """Возвращает список всех агентов из реестра."""
        agents = self.registry.get("agents", {})
        return json.dumps(agents, ensure_ascii=False, indent=2)

    async def get_agent_info(self, agent_name: str) -> str:
        """Возвращает информацию об агенте по имени (или ID)."""
        agents = self.registry.get("agents", {})
        # Поиск по ID или по display_name
        for aid, info in agents.items():
            if aid == agent_name or info.get("name", "").lower() == agent_name.lower():
                return json.dumps(info, ensure_ascii=False)
        return json.dumps({"error": f"Агент '{agent_name}' не найден в реестре."})

    async def analyze_agent_code(self, agent_name: str) -> str:
        """Анализирует код агента (заглушка, позже можно вызвать модель)."""
        # Пока просто проверяем существование папки
        agent_path = self._get_agent_path(agent_name)
        if not agent_path.exists():
            return json.dumps({"error": f"Папка агента {agent_name} не найдена."})
        return json.dumps({
            "status": "ok",
            "message": f"Анализ кода агента {agent_name} пока не реализован. Но я могу посоветовать: проверь, есть ли в агенте инструменты и правильно ли они описаны."
        })

    async def create_agent_structure(self, name: str, display_name: str, description: str = "") -> str:
        """
        Создаёт базовую структуру для нового агента.
        - name: идентификатор (латиница, без пробелов)
        - display_name: имя для отображения (например, "Новый агент")
        - description: краткое описание (необязательно)
        """
        base_path = self._get_agent_path(name)
        if base_path.exists():
            return json.dumps({"error": f"Агент с именем '{name}' уже существует."})

        try:
            # Создаём основные папки
            (base_path / "app").mkdir(parents=True)
            (base_path / "app/__init__.py").touch()

            # --- agent.py ---
            agent_template = f'''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class {display_name.replace(' ', '')}Agent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "{display_name}"

    # TODO: добавить инструменты
'''
            (base_path / "app/agent.py").write_text(agent_template, encoding='utf-8')

            # --- config.yaml ---
            config = {
                "agent": {
                    "name": display_name,
                    "system_prompt": f"Ты — {display_name}. ... (опиши роль)"
                },
                "api": {
                    "provider": "n1n",
                    "key_env": "API_KEY",
                    "base_url": "https://api.n1n.ai/v1",
                    "model": "qwen3-coder-480b-a35b-instruct"
                },
                "paths": {
                    "data_root": "~/ai-agents/data",
                    "agent_data": name
                },
                "tools": []
            }
            with open(base_path / "config.yaml", 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False)

            # --- main.py ---
            main_code = f'''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from service_base import create_agent_app
from .agent import {display_name.replace(' ', '')}Agent

app = create_agent_app(
    agent_class={display_name.replace(' ', '')}Agent,
    service_name="{name}",
    default_port=8000,
    telegram_token_env="{name.upper()}_TOKEN"
)
'''
            (base_path / "app/main.py").write_text(main_code, encoding='utf-8')

            # --- run.sh ---
            run_script = f'''#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
'''
            (base_path / "run.sh").write_text(run_script, encoding='utf-8')
            (base_path / "run.sh").chmod(0o755)

            # --- .env ---
            (base_path / ".env").write_text("# API_KEY=your_key_here\n", encoding='utf-8')

            # --- requirements.txt (копируем из architect) ---
            src_req = Path(__file__).parent.parent / "requirements.txt"
            if src_req.exists():
                shutil.copy2(src_req, base_path / "requirements.txt")
            else:
                # если нет, создаём базовый
                (base_path / "requirements.txt").write_text(
                    "-r ../core_requirements.txt\n",
                    encoding='utf-8'
                )

            # После успешного создания можно обновить реестр (но оставим это на усмотрение)
            # Вернём информацию о созданной структуре
            return json.dumps({
                "status": "ok",
                "message": f"✅ Структура для агента '{display_name}' создана в {base_path}",
                "path": str(base_path)
            })
        except Exception as e:
            self.logger.error(f"Ошибка при создании агента: {e}")
            return json.dumps({"error": f"Не удалось создать агента: {str(e)}"})

    async def update_registry(self, agent_id: str, data: Dict) -> str:
        """Добавляет или обновляет запись об агенте в реестре."""
        if "agents" not in self.registry:
            self.registry["agents"] = {}
        self.registry["agents"][agent_id] = data
        self._save_registry()
        return json.dumps({"status": "ok", "message": f"Запись об агенте {agent_id} обновлена в реестре."})