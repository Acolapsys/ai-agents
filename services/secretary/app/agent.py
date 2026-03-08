# ~/ai-agents/services/secretary/app/agent.py
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class SecretaryAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)

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