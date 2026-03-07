import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Загружаем переменные из .env, который лежит на уровень выше (рядом с run.sh)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class SecretaryAgent:
    def __init__(self):
        self.name = "Михаил"

        # Приоритет: сначала OpenRouter, потом n1n
        self.api_key = os.environ.get("N1N_API_KEY") or os.environ.get("N1N_API_KEY")
        self.base_url = os.environ.get("N1N_BASE_URL", "https://api.n1n.ai/v1")
        self.model = os.environ.get("N1N_MODEL", "qwen3-coder-480b-a35b-instruct")

        if not self.api_key:
            raise ValueError("Не задан API-ключ! Укажите OPENROUTER_API_KEY или N1N_API_KEY в .env")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # Пути к данным
        self.data_path = Path.home() / "ai-agents" / "data" / "secretary"
        self.notes_path = self.data_path / "notes"
        self.tasks_path = self.data_path / "tasks"
        self.reminders_path = self.data_path / "reminders"
        self.memory_path = self.data_path / "memory"

        for p in [self.notes_path, self.tasks_path, self.reminders_path, self.memory_path]:
            p.mkdir(parents=True, exist_ok=True)

        self.conversations = self._load_conversations()
        self.tools = self._get_tools()

    def _load_conversations(self) -> Dict[str, List]:
        conv_file = self.memory_path / "conversations.json"
        if conv_file.exists():
            with open(conv_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_conversations(self):
        conv_file = self.memory_path / "conversations.json"
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)

    def _add_message(self, chat_id: str, role: str, content: str):
        if chat_id not in self.conversations:
            self.conversations[chat_id] = []
        self.conversations[chat_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.conversations[chat_id]) > 50:
            self.conversations[chat_id] = self.conversations[chat_id][-50:]
        self._save_conversations()

    def _get_history(self, chat_id: str, limit: int = 10) -> List[Dict]:
        if chat_id not in self.conversations:
            return []
        return self.conversations[chat_id][-limit:]

    def _get_tools(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "save_note",
                    "description": "Сохраняет заметку в файл",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Текст заметки"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_shopping_list",
                    "description": "Добавляет товар в список покупок",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string", "description": "Название товара"},
                            "quantity": {"type": "integer", "description": "Количество", "default": 1}
                        },
                        "required": ["item"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_reminder",
                    "description": "Создаёт напоминание",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Текст напоминания"},
                            "time": {"type": "string", "description": "Время в формате HH:MM или относительное"}
                        },
                        "required": ["text", "time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Добавляет задачу в список дел",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "Описание задачи"}
                        },
                        "required": ["task"]
                    }
                }
            }
        ]

    async def _save_note(self, content: str) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        note_file = self.notes_path / f"{today}.txt"
        with open(note_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time_str}] {content}\n")
        return f"Заметка сохранена: {content[:50]}..."

    async def _add_to_shopping_list(self, item: str, quantity: int = 1) -> str:
        shopping_file = self.tasks_path / "shopping.txt"
        item_line = f"• {item}" + (f" x{quantity}" if quantity > 1 else "") + "\n"
        with open(shopping_file, 'a', encoding='utf-8') as f:
            f.write(item_line)
        return f"Добавлено в список покупок: {item}" + (f" в количестве {quantity}" if quantity > 1 else "")

    async def _create_reminder(self, text: str, time: str) -> str:
        reminder_file = self.reminders_path / "reminders.txt"
        with open(reminder_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {time} | {text}\n")
        return f"Напоминание создано: {text} на {time}"

    async def _add_task(self, task: str) -> str:
        task_file = self.tasks_path / "tasks.txt"
        with open(task_file, 'a', encoding='utf-8') as f:
            f.write(f"[ ] {task}\n")
        return f"Задача добавлена: {task}"

    async def execute_tool(self, tool_call: Dict) -> Dict:
        func_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        if func_name == "save_note":
            result = await self._save_note(**arguments)
        elif func_name == "add_to_shopping_list":
            result = await self._add_to_shopping_list(**arguments)
        elif func_name == "create_reminder":
            result = await self._create_reminder(**arguments)
        elif func_name == "add_task":
            result = await self._add_task(**arguments)
        else:
            result = f"Неизвестный инструмент: {func_name}"

        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": result
        }

    async def process_message(self, message: str, user_id: str, chat_id: str) -> str:
        history = self._get_history(chat_id)
        system_prompt = f"Ты — {self.name}, личный секретарь. Ты помогаешь с задачами, заметками, списком покупок и напоминаниями. Отвечай кратко и по делу."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=4096
            )
        except Exception as e:
            return f"Ошибка вызова модели: {str(e)}"

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append(assistant_message)
            for tool_call in assistant_message.tool_calls:
                tool_result = await self.execute_tool(tool_call.model_dump())
                messages.append(tool_result)

            try:
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096
                )
                final_answer = final_response.choices[0].message.content
            except Exception as e:
                final_answer = f"Ошибка при генерации финального ответа: {str(e)}"
        else:
            final_answer = assistant_message.content

        self._add_message(chat_id, "user", message)
        self._add_message(chat_id, "assistant", final_answer)
        return final_answer


    async def handle_message(self, update, context):
        """Обработчик для Telegram-бота – адаптирует вызов к process_message"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        response = await self.process_message(message_text, user_id, chat_id)
        await update.message.reply_text(response)