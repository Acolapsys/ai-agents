#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import aiohttp
import json
import re
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import deque

sys.path.append(str(Path(__file__).parent.parent.parent))

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from core.agent import BaseAgent

class SecretaryAgent(BaseAgent):
    """
    Агент-секретарь Михаил с памятью и пониманием вопросов.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        print("🟢 SecretaryAgent.__init__: start")
        super().__init__(config_path)
        
        self.display_name = "Михаил"
        
        # Хранилища
        self.notes_path = self.get_storage_path('notes')
        self.tasks_path = self.get_storage_path('tasks')
        self.reminders_path = self.get_storage_path('reminders')
        self.memory_path = self.get_storage_path('memory')
        
        self.notes_path.mkdir(exist_ok=True)
        self.tasks_path.mkdir(exist_ok=True)
        self.reminders_path.mkdir(exist_ok=True)
        self.memory_path.mkdir(exist_ok=True)
        
        # Загружаем историю разговоров
        self.conversation_history = self._load_conversation_history()
        
        # Текущий контекст (последние 10 сообщений)
        self.current_context = deque(maxlen=10)
        
        # Планировщик напоминаний
        self.reminders = self.load_yaml('reminders', 'active.yaml', default=[])
        
        # Очередь для напоминаний
        self.reminder_queue = deque()
        
        # Флаг проверки Ollama
        self.ollama_checked = False
        
        self.logger.info(f"✅ Агент {self.display_name} инициализирован")
        print("🟢 SecretaryAgent.__init__: end")
    
    def _load_conversation_history(self) -> Dict[str, List]:
        """Загружает историю разговоров для разных чатов"""
        history_file = self.memory_path / 'conversations.json'
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_conversation_history(self):
        """Сохраняет историю разговоров"""
        history_file = self.memory_path / 'conversations.json'
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
    
    def _add_to_context(self, chat_id: str, role: str, message: str):
        """Добавляет сообщение в контекст"""
        if chat_id not in self.conversation_history:
            self.conversation_history[chat_id] = []
        
        entry = {
            'time': datetime.now().isoformat(),
            'role': role,
            'text': message
        }
        self.conversation_history[chat_id].append(entry)
        
        if len(self.conversation_history[chat_id]) > 50:
            self.conversation_history[chat_id] = self.conversation_history[chat_id][-50:]
        
        self._save_conversation_history()
        self.current_context.append(f"{role}: {message}")
    
    def _get_recent_context(self, chat_id: str, limit: int = 5) -> str:
        """Возвращает последние сообщения из контекста"""
        if chat_id not in self.conversation_history:
            return ""
        
        recent = self.conversation_history[chat_id][-limit:]
        return "\n".join([f"{msg['role']}: {msg['text']}" for msg in recent])
    
    def _is_question(self, text: str) -> bool:
        """Определяет, является ли текст вопросом"""
        text_lower = text.lower()
        
        # Вопросительные слова
        question_words = ['где', 'когда', 'почему', 'зачем', 'как', 'что', 'кто', 
                         'какой', 'какая', 'какое', 'какие', 'сколько', 'чей']
        
        # Проверяем наличие вопросительных слов в начале или вопросительный знак
        words = text_lower.split()
        if words and words[0] in question_words:
            return True
        
        if '?' in text or '?' in text:
            return True
        
        return False
    
    def _is_shopping_command(self, text: str) -> bool:
        """Определяет, является ли текст командой для списка покупок"""
        text_lower = text.lower()
        shopping_indicators = ['купить', 'добавь в список', 'надо купить', 'нужно купить']
        
        # Проверяем точное начало
        if any(text_lower.startswith(word) for word in shopping_indicators):
            return True
        
        # Проверяем наличие ключевых слов в начале
        words = text_lower.split()
        if len(words) >= 2 and words[0] in ['купить', 'добавь']:
            return True
        
        return False
    
    def _is_task_command(self, text: str) -> bool:
        """Определяет, является ли текст командой для задач"""
        text_lower = text.lower()
        task_indicators = ['задача', 'сделать', 'нужно сделать']
        return any(text_lower.startswith(word) for word in task_indicators)
    
    def _is_note_command(self, text: str) -> bool:
        """Определяет, является ли текст командой для заметок"""
        text_lower = text.lower()
        note_indicators = ['запиши', 'заметка', 'сохрани']
        return any(text_lower.startswith(word) for word in note_indicators)
    
    def _is_reminder_command(self, text: str) -> bool:
        """Определяет, является ли текст командой для напоминаний"""
        text_lower = text.lower()
        reminder_indicators = ['напомни', 'не забудь']
        return any(text_lower.startswith(word) for word in reminder_indicators)
    
    def check_reminders(self):
        """Проверяет активные напоминания"""
        try:
            self.reminders = self.load_yaml('reminders', 'active.yaml', default=[])
            current_time = self.get_current_time()
            current_date = self.get_current_date()
            
            for reminder in self.reminders:
                if not reminder.get('active', True):
                    continue
                
                reminder_time = reminder.get('time')
                reminder_date = reminder.get('date', current_date)
                
                if reminder_date == current_date and reminder_time == current_time:
                    self.logger.info(f"🔔 Сработало напоминание: {reminder.get('message')}")
                    self.reminder_queue.append(reminder)
                    
                    if not reminder.get('recurring', False):
                        reminder['active'] = False
                        self.save_yaml(self.reminders, 'reminders', 'active.yaml')
                    
        except Exception as e:
            self.logger.error(f"Ошибка в check_reminders: {e}")
    
    def start_scheduler(self):
        """Запускает планировщик"""
        import schedule
        import time
        
        def run_scheduler():
            schedule.every(1).minutes.do(self.check_reminders)
            while True:
                schedule.run_pending()
                time.sleep(10)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        self.logger.info("⏰ Планировщик запущен")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает входящие сообщения"""
        if not update.message or not update.message.text:
            return
        
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        message = update.message.text.strip()
        
        self.logger.info(f"📨 Сообщение от {user.first_name}: {message[:50]}...")
        
        # Сохраняем сообщение пользователя
        self._add_to_context(chat_id, user.first_name or "Пользователь", message)
        
        # Обрабатываем запрос
        response = await self._process_request(message, user.first_name, chat_id)
        
        # Сохраняем ответ
        self._add_to_context(chat_id, self.display_name, response)
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def _process_request(self, message: str, user_name: str, chat_id: str) -> str:
        """Обрабатывает запрос с учётом контекста"""
        message_lower = message.lower()
        
        # Базовые команды
        if message_lower in ['/start', 'start', 'привет', 'здравствуй']:
            return self._get_welcome()
        
        if message_lower in ['/help', 'помощь', 'что ты умеешь']:
            return self._get_help()
        
        if message_lower in ['контекст', 'история', 'что мы обсуждали']:
            return self._show_context(chat_id)
        
        # Проверяем, является ли сообщение вопросом
        if self._is_question(message):
            return await self._answer_question(message, user_name, chat_id)
        
        # Команды для списка покупок
        if self._is_shopping_command(message):
            return await self._handle_shopping(message)
        
        if message_lower in ['что купить', 'список покупок', 'покажи покупки']:
            return await self._show_shopping()
        
        # Команды для задач
        if self._is_task_command(message):
            return await self._handle_task(message)
        
        if message_lower in ['задачи', 'какие задачи', 'покажи задачи']:
            return await self._show_tasks()
        
        # Команды для заметок
        if self._is_note_command(message):
            return await self._handle_note(message)
        
        if message_lower in ['заметки', 'покажи заметки']:
            return await self._show_notes()
        
        # Команды для напоминаний
        if self._is_reminder_command(message):
            return await self._handle_reminder(message)
        
        # Если ничего не подошло, пытаемся использовать нейросеть
        return await self._answer_question(message, user_name, chat_id)
    
    async def _answer_question(self, message: str, user_name: str, chat_id: str) -> str:
        """Отвечает на вопрос с помощью нейросети"""
        # Проверяем доступность Ollama
        if not self.ollama_checked:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://localhost:11434/api/tags', timeout=2) as resp:
                        self.ollama_checked = (resp.status == 200)
            except:
                self.ollama_checked = False
        
        if not self.ollama_checked:
            return ("🔌 Нейросеть не доступна. Я могу только:\n"
                   "• добавлять в список покупок (купить ...)\n"
                   "• создавать задачи (задача ...)\n"
                   "• делать заметки (запиши ...)\n"
                   "• ставить напоминания (напомни ...)\n\n"
                   "Или попробуй позже, когда Ollama запустится.")
        
        context = self._get_recent_context(chat_id, limit=5)
        
        prompt = f"""Ты — Михаил, личный секретарь. Ты бывший военный, поэтому говоришь чётко, по делу, структурированно.

Контекст разговора:
{context}

Пользователь {user_name} задал вопрос: {message}

Если вопрос про время, дату, погоду - ответь, но предупреди, что информация может быть неточной.
Если вопрос про покупки - предложи добавить в список.
Если вопрос про задачи - предложи создать задачу.

Ответь кратко и по делу:"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': 'qwen2.5:7b',
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.7,
                            'num_predict': 300
                        }
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get('response', '')
                        if answer:
                            return answer
        except Exception as e:
            self.logger.error(f"Ошибка при вызове Ollama: {e}")
        
        return "Извините, не могу сейчас ответить на вопрос. Попробуйте использовать команды."
    
    def _show_context(self, chat_id: str) -> str:
        """Показывает историю разговора"""
        context = self._get_recent_context(chat_id, limit=10)
        if not context:
            return "📭 История пока пуста"
        return f"📝 *Последние сообщения:*\n\n{context}"
    
    async def _handle_note(self, message: str) -> str:
        """Сохраняет заметку"""
        note_text = message
        for word in ['запиши', 'заметка', 'сохрани']:
            note_text = note_text.replace(word, '')
        note_text = note_text.strip()
        
        if not note_text:
            return "Что записать?"
        
        today = self.get_current_date()
        time_now = self.get_current_time()
        note_entry = f"[{time_now}] {note_text}\n"
        
        self.append_text(note_entry, 'notes', f"{today}.txt")
        return f"✅ Заметка сохранена"
    
    async def _show_notes(self) -> str:
        """Показывает сегодняшние заметки"""
        today = self.get_current_date()
        notes = self.read_text('notes', f"{today}.txt")
        
        if not notes.strip():
            return f"📭 Заметок за {today} нет"
        
        return f"📝 *Заметки за {today}:*\n{notes}"
    
    async def _handle_shopping(self, message: str) -> str:
        """Добавляет в список покупок"""
        # Извлекаем текст покупки
        item = message
        for word in ['купить', 'добавь в список', 'надо купить', 'нужно купить']:
            item = item.replace(word, '')
        item = item.strip()
        
        if not item or item.lower() in ['список', 'покупки']:
            return "Что именно купить?"
        
        # Форматируем для красоты
        item = item[0].upper() + item[1:] if item else ""
        
        self.append_text(f"• {item}\n", 'tasks', 'shopping.txt')
        return f"✅ '{item}' добавлен в список покупок"
    
    async def _show_shopping(self) -> str:
        """Показывает список покупок"""
        items = self.read_text('tasks', 'shopping.txt')
        if items.strip():
            return f"🛒 *Список покупок:*\n{items}"
        return "🛒 Список покупок пуст"
    
    async def _handle_task(self, message: str) -> str:
        """Добавляет задачу"""
        task_text = message
        for word in ['задача', 'сделать', 'нужно сделать']:
            task_text = task_text.replace(word, '')
        task_text = task_text.strip()
        
        if not task_text:
            return "Что нужно сделать?"
        
        task_text = task_text[0].upper() + task_text[1:] if task_text else ""
        
        self.append_text(f"[ ] {task_text}\n", 'tasks', 'tasks.txt')
        return f"✅ Задача добавлена: {task_text}"
    
    async def _show_tasks(self) -> str:
        """Показывает задачи"""
        tasks = self.read_text('tasks', 'tasks.txt')
        if tasks.strip():
            return f"📋 *Задачи:*\n{tasks}"
        return "📋 Задач пока нет"
    
    async def _handle_reminder(self, message: str) -> str:
        """Создаёт напоминание"""
        # Парсим время
        reminder_time = "09:00"
        reminder_text = message
        
        time_match = re.search(r'в (\d{1,2}):(\d{2})', message)
        if time_match:
            reminder_time = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"
            reminder_text = re.sub(r'в \d{1,2}:\d{2}', '', message).strip()
        
        for word in ['напомни', 'не забудь']:
            reminder_text = reminder_text.replace(word, '').strip()
        
        if not reminder_text:
            reminder_text = "Напоминание"
        
        reminders = self.load_yaml('reminders', 'active.yaml', default=[])
        reminders.append({
            'id': len(reminders) + 1,
            'message': reminder_text,
            'date': self.get_current_date(),
            'time': reminder_time,
            'active': True
        })
        self.save_yaml(reminders, 'reminders', 'active.yaml')
        
        return f"⏰ Напоминание на {reminder_time}: {reminder_text}"
    
    def _get_welcome(self) -> str:
        return (f"Здравия желаю, {self.user_name}! Я {self.display_name}, секретарь.\n\n"
                f"Я понимаю:\n"
                f"• вопросы (где, когда, почему)\n"
                f"• команды (купить, задача, запиши, напомни)\n\n"
                f"Напиши 'помощь' для списка команд.")
    
    def _get_help(self) -> str:
        return ("*Команды:*\n\n"
                "📝 *Заметки:*\n"
                "• запиши [текст]\n"
                "• заметки — показать\n\n"
                "🛒 *Покупки:*\n"
                "• купить [товар]\n"
                "• что купить — список\n\n"
                "📋 *Задачи:*\n"
                "• задача [текст]\n"
                "• задачи — показать\n\n"
                "⏰ *Напоминания:*\n"
                "• напомни [что]\n"
                "• напомни в [время] [что]\n\n"
                "❓ *Другое:*\n"
                "• контекст — история\n"
                "• любой вопрос — постараюсь ответить")


def main():
    print("🚀 Запуск Михаила...")
    
    token = os.environ.get('SECRETARY_TOKEN')
    if not token:
        token_file = Path.home() / 'ai-agents' / 'config' / 'tokens.env'
        if token_file.exists():
            with open(token_file, 'r') as f:
                for line in f:
                    if line.startswith('SECRETARY_TOKEN='):
                        token = line.strip().split('=', 1)[1].strip()
                        break
    
    if not token:
        print("❌ Токен не найден!")
        return
    
    agent = SecretaryAgent()
    agent.start_scheduler()
    
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_message))
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")

if __name__ == '__main__':
    main()
