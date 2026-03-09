#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import re
import traceback

# Добавляем путь к корневой папке проекта
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path.home() / "ai-agents/src"))

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from core.agent import BaseAgent

class EnglishMentorAgent(BaseAgent):
    """
    Виктор Иванович Лингвист - персональный учитель английского языка
    """

    def __init__(self, config_path: Optional[str] = None):
        print("🇬🇧 EnglishMentorAgent.__init__: start")

        # Вызываем родительский конструктор
        super().__init__(config_path)

        # Переопределяем имя для отображения
        self.display_name = "Виктор Иванович Лингвист"

        # Создаём папки для хранения данных обучения
        self.learning_path = self.get_storage_path('learning')
        self.learning_path.mkdir(exist_ok=True)

        # Загружаем профиль ученика
        self.student_profile = self._load_student_profile()

        # Загружаем историю уроков
        self.lesson_history = self._load_lesson_history()

        # Текущий урок (если есть)
        self.current_lesson = None

        # Флаг для проверки Ollama (будет установлен позже)
        self.ollama_checked = False

        self.logger.info(f"✅ Агент {self.display_name} инициализирован")
        print("🇬🇧 EnglishMentorAgent.__init__: end")

    async def _check_ollama_connection(self):
        """Проверяет подключение к Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', timeout=5) as response:
                    if response.status == 200:
                        self.logger.info("✅ Подключение к Ollama установлено")
                        self.ollama_checked = True
                        return True
                    else:
                        self.logger.error(f"❌ Ollama вернула статус {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Не удалось подключиться к Ollama: {e}")
            self.logger.info("💡 Запустите Ollama командой: ollama serve")

        self.ollama_checked = False
        return False

    def _load_student_profile(self) -> Dict:
        """Загружает или создаёт профиль ученика"""
        profile_file = self.learning_path / 'profile.json'

        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Создаём новый профиль
        profile = {
            'name': self.user_name,
            'level': 'beginner',
            'goal': 'Разговорный английский для работы',
            'strengths': [],
            'weaknesses': [],
            'vocabulary_size': 0,
            'lessons_completed': 0,
            'total_time': 0,
            'last_lesson': None,
            'preferences': {
                'topics': ['технологии', 'путешествия', 'бизнес'],
                'lesson_duration': 20,
                'correction_style': 'gentle'
            },
            'progress': {
                'grammar': {},
                'vocabulary': {},
                'speaking': {},
                'listening': {}
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self._save_student_profile(profile)
        return profile

    def _save_student_profile(self, profile: Dict):
        """Сохраняет профиль ученика"""
        profile['updated_at'] = datetime.now().isoformat()
        profile_file = self.learning_path / 'profile.json'
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def _load_lesson_history(self) -> List[Dict]:
        """Загружает историю уроков"""
        history_file = self.learning_path / 'lessons.json'

        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_lesson(self, lesson_data: Dict):
        """Сохраняет урок в историю"""
        self.lesson_history.append(lesson_data)
        history_file = self.learning_path / 'lessons.json'
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.lesson_history[-50:], f, ensure_ascii=False, indent=2)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает входящие сообщения"""
        if not update.message or not update.message.text:
            return

        user = update.effective_user
        message = update.message.text.strip()

        self.logger.info(f"📨 Сообщение от {user.first_name}: {message[:50]}...")

        # Сохраняем context для уведомлений
        if not hasattr(self, 'application'):
            self.application = context.application
            self.chat_id = update.effective_chat.id

        # Проверяем Ollama при первом сообщении
        if not self.ollama_checked:
            await self._check_ollama_connection()

        # Определяем тип запроса
        try:
            response = await self._process_request(message, user.first_name)
            await update.message.reply_text(response, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"❌ Ошибка при обработке: {e}")
            self.logger.error(traceback.format_exc())
            await update.message.reply_text("Извините, произошла внутренняя ошибка. Попробуйте позже.")

    async def process_message(self, text: str, user_id: str, chat_id: str) -> str:
        # Используем существующий метод, подставив фейковый update
        # Либо переиспользуем внутреннюю логику _process_request
        return await self._process_request(text, user_id)  # пример

    async def _process_request(self, message: str, user_name: str) -> str:
        """Обрабатывает запрос к учителю"""
        message_lower = message.lower()

        # Команды
        if message_lower in ['/start', 'start', 'привет', 'здравствуйте']:
            return self._get_welcome()

        if message_lower in ['/help', 'помощь', 'что ты умеешь']:
            return self._get_help()

        if message_lower in ['профиль', 'мой прогресс', 'статистика']:
            return self._show_profile()

        if message_lower.startswith('урок'):
            return await self._start_lesson(message)

        if message_lower in ['завершить урок', 'хватит', 'стоп', 'закончить']:
            return self._end_lesson()

        if message_lower in ['слова', 'мои слова', 'словарь']:
            return self._show_vocabulary()

        if message_lower.startswith('добавь слово'):
            return await self._add_word(message)

        # Если есть текущий урок - продолжаем его
        if self.current_lesson:
            return await self._continue_lesson(message)

        # Общий разговор - обучаем
        return await self._teach(message, user_name)

    async def _start_lesson(self, message: str) -> str:
        """Начинает новый урок"""
        # Определяем тему, если указана
        topic = message.replace('урок', '').strip()

        # Создаём новый урок
        self.current_lesson = {
            'started_at': datetime.now().isoformat(),
            'topic': topic if topic else 'general',
            'messages': [],
            'exercises': [],
            'score': 0,
            'new_words': []
        }

        self.logger.info(f"🎯 Начат новый урок по теме: {self.current_lesson['topic']}")

        # Проверяем доступность Ollama
        if not self.ollama_checked:
            await self._check_ollama_connection()

        if not self.ollama_checked:
            return ("🔌 *Нейросеть не доступна*\n\n"
                   "Не могу начать урок без подключения к Ollama.\n"
                   "Пожалуйста, запустите Ollama командой `ollama serve` в терминале.")

        # Генерируем вступление
        prompt = f"""You are an English teacher. Start a new lesson for a {self.student_profile['level']} level student.

Student's goal: {self.student_profile['goal']}
Topic: {topic if topic else 'general conversation'}

Generate a warm welcome in Russian (but with some English examples) and the first exercise or question.
Keep it engaging and appropriate for their level.
Make it personal - address the student by name: {self.user_name}

The response should be helpful and educational."""

        response = await self._call_ollama(prompt)
        return f"📚 *Начинаем урок!*\n\n{response}"

    async def _continue_lesson(self, message: str) -> str:
        """Продолжает текущий урок"""
        if not self.current_lesson:
            return await self._teach(message, self.user_name)

        self.logger.info(f"📝 Продолжение урока. Ответ ученика: {message[:50]}...")

        # Проверяем доступность Ollama
        if not self.ollama_checked:
            await self._check_ollama_connection()

        if not self.ollama_checked:
            return ("🔌 *Нейросеть не доступна*\n\n"
                   "Не могу продолжить урок без подключения к Ollama.\n"
                   "Пожалуйста, запустите Ollama командой `ollama serve` в терминале.")

        # Добавляем сообщение в историю урока
        self.current_lesson['messages'].append({
            'time': datetime.now().isoformat(),
            'student': message
        })

        # Анализируем ответ
        analysis_prompt = f"""You are an experienced English teacher. Analyze this student response in the current lesson context.

Student's name: {self.user_name}
Student's level: {self.student_profile['level']}
Lesson started at: {self.current_lesson['started_at']}
Topic: {self.current_lesson['topic']}

Student's response: "{message}"

Provide a helpful teacher's response that:
1. Corrects any mistakes gently (if any)
2. Praises what was done well
3. Gives a brief explanation if needed
4. Continues the conversation with a new question or exercise

Respond in Russian, using English examples. Be encouraging and educational."""

        response = await self._call_ollama(analysis_prompt)

        # Добавляем ответ учителя в историю
        self.current_lesson['messages'].append({
            'time': datetime.now().isoformat(),
            'teacher': response[:100]  # сохраняем только начало для истории
        })

        return response

    def _end_lesson(self) -> str:
        """Завершает текущий урок"""
        if not self.current_lesson:
            return "Урок ещё не начат. Напиши 'урок' чтобы начать!"

        # Сохраняем урок
        self.current_lesson['ended_at'] = datetime.now().isoformat()
        duration = (datetime.fromisoformat(self.current_lesson['ended_at']) -
                   datetime.fromisoformat(self.current_lesson['started_at'])).seconds // 60

        # Обновляем статистику
        self.student_profile['lessons_completed'] += 1
        self.student_profile['total_time'] += duration
        self.student_profile['last_lesson'] = datetime.now().isoformat()

        self._save_lesson(self.current_lesson)
        self._save_student_profile(self.student_profile)

        summary = f"""📊 *Урок завершён!*

⏱ Длительность: {duration} минут
📚 Новых слов: {len(self.current_lesson.get('new_words', []))}
🎯 Всего уроков: {self.student_profile['lessons_completed']}

Хочешь продолжить позже? Просто напиши 'урок' когда будешь готов!"""

        self.logger.info(f"✅ Урок завершён. Длительность: {duration} мин")
        self.current_lesson = None
        return summary

    async def _teach(self, message: str, user_name: str) -> str:
        """Обучает в разговорном режиме"""

        # Проверяем доступность Ollama
        if not self.ollama_checked:
            await self._check_ollama_connection()

        if not self.ollama_checked:
            return self._get_fallback_response()

        # Получаем контекст из профиля
        level = self.student_profile['level']

        prompt = f"""You are Виктор Иванович Лингвист, an experienced English teacher. You are having a conversation with your student.

Student profile:
- Name: {user_name}
- Level: {level}
- Learning goal: {self.student_profile['goal']}

Teaching guidelines:
1. Correct mistakes gently
2. Explain grammar when needed
3. Introduce new vocabulary naturally
4. Encourage the student
5. Adapt language to their level

Student wrote: {message}

Respond as a teacher - in Russian, but with English examples and corrections. Make it educational and encouraging."""

        return await self._call_ollama(prompt)

    def _show_profile(self) -> str:
        """Показывает профиль и прогресс"""
        profile = self.student_profile

        # Определяем уровень
        level_emoji = {
            'beginner': '🌱',
            'elementary': '🌿',
            'intermediate': '🌳',
            'upper-intermediate': '🌲',
            'advanced': '🎓'
        }

        # Вычисляем примерный размер словарного запаса
        vocab_size = len(profile['progress'].get('vocabulary', {}))

        result = f"""📊 *Ваш профиль обучения*

{level_emoji.get(profile['level'], '📚')} *Уровень:* {profile['level'].upper()}
🎯 *Цель:* {profile['goal']}
📝 *Уроков пройдено:* {profile['lessons_completed']}
⏱ *Всего времени:* {profile['total_time']} минут
📚 *Словарный запас:* ~{vocab_size} слов

*Сильные стороны:*
{self._format_list(profile['strengths']) if profile['strengths'] else '  Ещё определяем...'}

*Над чем работать:*
{self._format_list(profile['weaknesses']) if profile['weaknesses'] else '  Скоро появятся рекомендации'}

*Любимые темы:*
{self._format_list(profile['preferences']['topics'])}

Хочешь начать урок? Напиши 'урок'!"""

        return result

    def _format_list(self, items: List[str]) -> str:
        """Форматирует список для вывода"""
        if not items:
            return "  Пока пусто"
        return '\n'.join([f"  • {item}" for item in items])

    def _show_vocabulary(self) -> str:
        """Показывает словарь"""
        vocab = self.student_profile['progress'].get('vocabulary', {})

        if not vocab:
            return "📚 Твой словарь пока пуст. Начни урок, и мы будем добавлять новые слова!"

        # Сортируем по дате
        sorted_words = sorted(vocab.items(), key=lambda x: x[1].get('learned', ''), reverse=True)[:20]

        result = "📚 *Твой словарь (последние 20 слов):*\n\n"
        for word, data in sorted_words:
            date = datetime.fromisoformat(data['learned']).strftime('%d.%m')
            result += f"• *{word}* — добавлено {date}\n"

        result += f"\nВсего слов: {len(vocab)}"
        return result

    async def _add_word(self, message: str) -> str:
        """Добавляет слово в словарь"""
        word = message.replace('добавь слово', '').strip()

        if not word:
            return "Какое слово добавить? Напиши: добавь слово [слово]"

        # Очищаем от лишнего
        word = re.sub(r'[^a-zA-Z\s-]', '', word).strip().lower()

        if not word:
            return "Пожалуйста, введите английское слово"

        vocab = self.student_profile['progress'].get('vocabulary', {})

        if word in vocab:
            return f"Слово '{word}' уже есть в твоём словаре!"

        vocab[word] = {
            'learned': datetime.now().isoformat(),
            'practice_count': 0
        }

        self.student_profile['progress']['vocabulary'] = vocab
        self._save_student_profile(self.student_profile)

        return f"✅ Слово '{word}' добавлено в твой словарь! Теперь у тебя {len(vocab)} слов."

    async def _call_ollama(self, prompt: str, model: str = "qwen2.5:7b", retries: int = 2) -> str:
        """Вызывает Ollama с повторными попытками"""
        self.logger.info(f"🤖 Вызов Ollama, модель: {model}")

        for attempt in range(retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'http://localhost:11434/api/generate',
                        json={
                            'model': model,
                            'prompt': prompt,
                            'stream': False,
                            'options': {
                                'temperature': 0.7,
                                'num_predict': 500
                            }
                        },
                        timeout=60
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            answer = result.get('response', '')
                            self.logger.info(f"✅ Получен ответ от Ollama, длина: {len(answer)}")
                            return answer
                        else:
                            self.logger.error(f"❌ Ollama вернула статус {response.status}, попытка {attempt + 1}")
                            if attempt < retries:
                                await asyncio.sleep(2)
                                continue
            except asyncio.TimeoutError:
                self.logger.error(f"⏰ Таймаут при вызове Ollama, попытка {attempt + 1}")
                if attempt < retries:
                    await asyncio.sleep(3)
                    continue
            except aiohttp.ClientConnectorError:
                self.logger.error(f"❌ Не удалось подключиться к Ollama, попытка {attempt + 1}")
                if attempt < retries:
                    await asyncio.sleep(3)
                    continue
            except Exception as e:
                self.logger.error(f"❌ Ошибка при вызове Ollama: {e}")
                if attempt < retries:
                    await asyncio.sleep(2)
                    continue

        self.logger.error("❌ Все попытки вызова Ollama исчерпаны")
        return self._get_fallback_response()

    def _get_welcome(self) -> str:
        """Приветственное сообщение"""
        return (f"Здравствуйте, {self.user_name}! Я {self.display_name}, ваш персональный учитель английского языка.\n\n"
                f"Я буду вести историю вашего обучения, отслеживать прогресс и подбирать уроки под ваш уровень.\n\n"
                f"📊 *Ваш текущий уровень:* {self.student_profile['level'].upper()}\n"
                f"🎯 *Цель:* {self.student_profile['goal']}\n\n"
                f"Напишите 'помощь' чтобы узнать, что я умею, или просто 'урок' чтобы начать заниматься!")

    def _get_help(self) -> str:
        """Справка по командам"""
        return (f"*Команды {self.display_name}:*\n\n"
                f"📚 *Обучение:*\n"
                f"• урок — начать новый урок\n"
                f"• завершить урок — закончить текущий\n"
                f"• профиль — мой прогресс\n"
                f"• слова — показать словарь\n"
                f"• добавь слово [слово] — добавить в словарь\n\n"
                f"💬 *Во время урока:*\n"
                f"• Просто общайся на английском\n"
                f"• Я буду исправлять ошибки\n"
                f"• Объяснять новые слова\n"
                f"• Подбирать упражнения\n\n"
                f"📊 *Уровни:*\n"
                f"🌱 beginner → 🌿 elementary → 🌳 intermediate → 🌲 upper-intermediate → 🎓 advanced\n\n"
                f"Готов начать? Напиши 'урок'!")

    def _get_fallback_response(self) -> str:
        """Заглушка, если нейросеть не доступна"""
        return ("🔌 *Нейросеть временно недоступна*\n\n"
                "Пожалуйста, проверьте:\n"
                "1. Запущена ли Ollama: `ollama serve`\n"
                "2. Доступны ли модели: `ollama list`\n\n"
                "Пока доступны команды:\n"
                "• 'профиль' — посмотреть прогресс\n"
                "• 'слова' — показать словарь\n"
                "• 'урок' — начать урок (когда нейросеть заработает)")


def main():
    """Запускает бота"""
    print("🚀 Запуск Виктора Ивановича Лингвиста...")

    # Получаем токен
    token = os.environ.get('ENGLISH_MENTOR_TOKEN')

    if not token:
        token_file = Path.home() / 'ai-agents' / 'config' / 'tokens.env'
        if token_file.exists():
            with open(token_file, 'r') as f:
                for line in f:
                    if line.startswith('ENGLISH_MENTOR_TOKEN='):
                        token = line.strip().split('=', 1)[1].strip()
                        break

    if not token:
        print("❌ Токен не найден!")
        return

    print(f"✅ Токен загружен")

    # Создаём агента
    agent = EnglishMentorAgent()

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_message))

    print("✅ Бот готов к работе!")
    print(f"📁 Логи сохраняются в: {Path.home() / 'ai-agents' / 'logs' / 'english_mentor' / 'agent.log'}")

    # Запускаем
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
