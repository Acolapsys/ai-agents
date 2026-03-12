# ~/ai-agents/services/secretary/app/agent.py
import sys
import aiohttp
import os
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class SecretaryAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.task_manager_url = os.environ.get('TASK_MANAGER_URL', 'http://localhost:8009')
        self.logger.info(f"Loaded tools: {[t['name'] for t in self.tools]}")

    # --- Реализации инструментов ---
    async def save_note(self, content: str) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        note_file = self.notes_path / f"{today}.txt"
        with open(note_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time_str}] {content}\n")
        return f"Заметка сохранена: {content[:50]}..."

    async def add_to_shopping_list(self, item: str, quantity: int = 1) -> str:
        shopping_file = self.tasks_path / "shopping.txt"
        item_line = f"• {item}" + (f" x{quantity}" if quantity > 1 else "") + "\n"
        with open(shopping_file, 'a', encoding='utf-8') as f:
            f.write(item_line)
        return f"Добавлено в список покупок: {item}" + (f" в количестве {quantity}" if quantity > 1 else "")

    async def create_reminder(self, text: str, time: str) -> str:
        reminder_file = self.reminders_path / "reminders.txt"
        with open(reminder_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {time} | {text}\n")
        return f"Напоминание создано: {text} на {time}"

    async def add_task(self, task: str) -> str:
        task_file = self.tasks_path / "tasks.txt"
        with open(task_file, 'a', encoding='utf-8') as f:
            f.write(f"[ ] {task}\n")
        return f"Задача добавлена: {task}"

    async def create_task(self, title: str, description: str = None, priority: str = 'medium') -> str:
        """Создаёт задачу в таск-трекере."""
        payload = {
            'title': title,
            'description': description,
            'priority': priority,
            'status': 'new',
            'assignee': 'user'  # или можно брать из контекста
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.task_manager_url}/tasks", json=payload) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        self.logger.info('1', data)
                        return json.dumps({"status": "ok", "task_id": data['id'], "message": f"Задача '{title}' создана"})
                    else:
                        error_text = await resp.text()
                        return json.dumps({"status": "error", "message": f"Ошибка создания задачи: {error_text}"})
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Не удалось связаться с таск-трекером по адресу {self.task_manager_url}: {str(e)}"
            })

    async def get_tasks(self, status: str = None, assignee: str = None) -> str:
        """Получает список задач с фильтрацией."""
        params = {}
        if status:
            params['status'] = status
        if assignee:
            params['assignee'] = assignee
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.task_manager_url}/tasks", params=params) as resp:
                    if resp.status == 200:
                        tasks = await resp.json()
                        return json.dumps({"status": "ok", "tasks": tasks})
                    else:
                        error_text = await resp.text()
                        return json.dumps({"status": "error", "message": f"Ошибка получения задач: {error_text}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Не удалось связаться с таск-трекером: {str(e)}"})