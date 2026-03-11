import os
import json
import logging
import time
from logging.handlers import RotatingFileHandler
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from openai import AsyncOpenAI

class BaseAgent:
    def __init__(self, config_path: str):
        # Загружаем конфиг
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.name = config['agent']['name']
        self.system_prompt = config['agent']['system_prompt']

        # Определяем agent_id как имя папки сервиса (родительская папка конфига)
        self.agent_id = Path(config_path).parent.name

        # Настройки API
        api_config = config['api']
        self.api_key = os.environ.get(api_config['key_env'])
        if not self.api_key:
            raise ValueError(f"Не задан ключ API: {api_config['key_env']}")

        self.base_url = api_config['base_url']
        self.model = api_config['model']
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

        # Пути к данным
        data_root = Path(config['paths']['data_root']).expanduser()
        self.agent_data_path = data_root / config['paths']['agent_data']
        self.notes_path = self.agent_data_path / "notes"
        self.tasks_path = self.agent_data_path / "tasks"
        self.reminders_path = self.agent_data_path / "reminders"
        self.memory_path = self.agent_data_path / "memory"

        for p in [self.notes_path, self.tasks_path, self.reminders_path, self.memory_path]:
            p.mkdir(parents=True, exist_ok=True)

        # Инструменты из конфига
        self.tools = config.get('tools', [])

        if self.tools:
            tools_description = "\n\nДоступные инструменты (только их и используй, других нет):\n"
            for tool in self.tools:
                name = tool['name']
                desc = tool.get('description', 'Нет описания')
                tools_description += f"- `{name}`: {desc}\n"
            tools_description += "\nЕсли ты вызовешь несуществующий инструмент, агент вернёт ошибку. Проанализируй ошибку и попробуй другой инструмент или попроси уточнить пользователя."

            # Добавляем к существующему system_prompt
            self.system_prompt += tools_description

        # Регистрация методов-обработчиков инструментов
        # Ожидается, что дочерний класс определит методы с именами, совпадающими с name в tools
        self.tool_handlers: Dict[str, Callable] = {}
        self._register_tool_handlers()

        # Логирование
        self.logger = logging.getLogger(self.name)
        self._setup_logging()
        debug_mode = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # Загрузка истории
        self.conversations = self._load_conversations()
        self.logger.info(f"🚀 Агент {self.name} инициализирован")

    def _setup_logging(self):
        """Настройка логирования в файл и консоль"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)

        # Единая папка для логов
        log_dir = Path.home() / "ai-agents" / "logs" / self.agent_id
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "agent.log"

        # Добавим ротацию, чтобы файл не рос бесконечно
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(file_handler)

        # Также выводим в консоль (уже настроено через basicConfig)

    def _register_tool_handlers(self):
        """Ищет в дочернем классе методы с именами, соответствующими инструментам"""
        for tool in self.tools:
            name = tool['name']
            handler = getattr(self, name, None)
            if handler and callable(handler):
                self.tool_handlers[name] = handler
            else:
                self.logger.warning(f"Для инструмента {name} не найден метод-обработчик")

    # --- Управление историей ---
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
        # Ограничим историю, например, последними 50 сообщениями
        if len(self.conversations[chat_id]) > 50:
            self.conversations[chat_id] = self.conversations[chat_id][-50:]
        self._save_conversations()

    def _get_history(self, chat_id: str, limit: int = 10) -> List[Dict]:
        if chat_id not in self.conversations:
            return []
        return self.conversations[chat_id][-limit:]

    def _get_tool_parameters(self, func_name: str) -> dict:
        """Возвращает описание параметров инструмента из конфига"""
        for tool in self.tools:
            if tool['name'] == func_name:
                return tool.get('parameters', {})
        return {}

    # --- Выполнение инструментов ---
    async def execute_tool(self, tool_call: Dict) -> Dict:
        """Выполняет инструмент по вызову от модели"""

        func_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        self.logger.info(f"🔧 Вызов инструмента {func_name} с аргументами: {arguments}")

        if func_name not in self.tool_handlers:
            result = json.dumps({
                "error": "unknown_tool",
                "message": f"Инструмент '{func_name}' не найден. Доступные инструменты: {list(self.tool_handlers.keys())}"
            })
        else:
            try:
                result = await self.tool_handlers[func_name](**arguments)
                self.logger.info(f"✅ Инструмент {func_name} выполнен успешно")
            except TypeError as e:
                # Ошибка несоответствия аргументов
                self.logger.error(f"❌ Ошибка выполнения {func_name}: {e}", exc_info=True)
                result = json.dumps({
                    "error": "invalid_arguments",
                    "message": f"Ошибка при вызове инструмента: {str(e)}",
                    "expected_parameters": self._get_tool_parameters(func_name)
                })
            except Exception as e:
                self.logger.error(f"Ошибка при выполнении {func_name}: {e}")
                result = json.dumps({
                    "error": "execution_error",
                    "message": f"Ошибка при выполнении {func_name}: {str(e)}"
                })
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": str(result)
        }

    # --- Основной метод обработки сообщения ---
    async def process_message(self, message: str, user_id: str, chat_id: str) -> str:
        """Основной цикл: история -> вызов модели -> обработка tool calls -> финальный ответ"""
        self.logger.info(f"📨 Входящее сообщение от {user_id}: {message[:50]}...")
        start_time = time.time()

        history = self._get_history(chat_id)

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=0.7,
                max_tokens=4096
            )
            duration = time.time() - start_time
            self.logger.info(f"✅ Модель ответила за {duration:.2f}с, токенов: {response.usage.total_tokens}")
        except Exception as e:
            self.logger.error(f"Ошибка вызова модели: {e}")
            return f"Извините, произошла ошибка при обращении к модели."

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                tool_result = await self.execute_tool(tool_call.model_dump())
                messages.append(tool_result)

            try:
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                )
                final_answer = final_response.choices[0].message.content

                duration = time.time() - start_time
                self.logger.info(f"✅ Финальный ответ за {duration:.2f}с, токенов: {final_response.usage.total_tokens}")
            except Exception as e:
                self.logger.error(f"Ошибка при генерации финального ответа: {e}")
                final_answer = "Извините, не удалось сформировать ответ после вызова инструментов."
        else:
            final_answer = assistant_message.content

        self._add_message(chat_id, "user", message)
        self._add_message(chat_id, "assistant", final_answer)
        return final_answer

    async def handle_telegram_message(self, update, context):
        """Обработчик для Telegram-бота – адаптирует вызов к process_message"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        response = await self.process_message(message_text, user_id, chat_id)
        await update.message.reply_text(response)