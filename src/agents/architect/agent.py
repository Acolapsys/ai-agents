#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Optional

# Добавляем путь к корневой папке проекта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from core.agent import BaseAgent

# Импортируем модули архитектора напрямую (не через пакет agents)
import agents.architect.utils as utils
import agents.architect.core_utils as core
import agents.architect.agent_creator as agent_creator
import agents.architect.code_manager as code_manager
import agents.architect.process_manager as process_manager

class ArchitectAgent(BaseAgent):
    """Главный архитектор Виктор"""

    def __init__(self, config_path: Optional[str] = None):
        print("🔷 ArchitectAgent.__init__: start")
        super().__init__(config_path)

        self.display_name = "Виктор"
        self.project_root = Path.home() / 'ai-agents'
        self.ollama_checked = False
        self.running_agents = {}

        # Загружаем реестр и шаблоны
        self.agents_registry = core.load_agents_registry(self.base_path)
        self.templates = core.load_templates(self.base_path)

        self.logger.info(f"✅ Агент {self.display_name} инициализирован")
        print("🔷 ArchitectAgent.__init__: end")

    async def _check_ollama_connection(self):
        """Проверяет подключение к Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', timeout=5) as response:
                    if response.status == 200:
                        self.logger.info("✅ Подключение к Ollama установлено")
                        self.ollama_checked = True
                        return True
        except Exception as e:
            self.logger.error(f"❌ Не удалось подключиться к Ollama: {e}")
        self.ollama_checked = False
        return False

    async def _call_ollama(self, prompt: str, model: str = "qwen2.5:14b", retries: int = 2) -> str:
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
                            'options': {'temperature': 0.7, 'num_predict': 2000}
                        },
                        timeout=120
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            answer = result.get('response', '')
                            self.logger.info(f"✅ Получен ответ от Ollama, длина: {len(answer)}")
                            return answer
            except asyncio.TimeoutError:
                self.logger.error(f"⏰ Таймаут, попытка {attempt + 1}")
            except Exception as e:
                self.logger.error(f"❌ Ошибка: {e}")

            if attempt < retries:
                await asyncio.sleep(3)

        return self._get_fallback_response("")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает входящие сообщения"""
        if not update.message or not update.message.text:
            return

        user = update.effective_user
        message = update.message.text.strip()

        self.logger.info(f"📨 Сообщение от {user.first_name}: {message[:50]}...")

        if not self.ollama_checked:
            await self._check_ollama_connection()

        response = await self._process_request(message, user.first_name)
        self.logger.info(f"📤 Ответ: {response[:50]}...")
        await update.message.reply_text(response, parse_mode='Markdown')

    async def _process_request(self, message: str, user_name: str) -> str:
        """Обрабатывает запрос к архитектору"""
        msg_lower = message.lower()

        # Базовые команды
        if msg_lower in ['/start', 'start', 'привет', 'здравствуй']:
            return self._get_welcome()
        if msg_lower in ['/help', 'помощь', 'что ты умеешь']:
            return self._get_help()

        # Список агентов
        if any(word in msg_lower for word in ['агенты', 'список агентов', 'кто есть']):
            return self._list_agents()

        # Информация об агенте
        if msg_lower.startswith('агент ') or msg_lower.startswith('кто такой '):
            return await self._get_agent_info(message)

        # Создание агента
        if (msg_lower.startswith('создай агента') or msg_lower.startswith('новый агент')):
            return await self._create_agent(message)

        # Добавление функционала
        if any(word in msg_lower for word in ['добавь функционал', 'добавь команду']):
            return await self._add_functionality(message)

        # Показать код
        if msg_lower.startswith('покажи код') or msg_lower.startswith('код агента'):
            return self._show_code(message)

        # Обновление агента
        if any(word in msg_lower for word in ['обнови агента', 'измени агента']):
            return await self._update_agent(message)

        # Шаблоны
        if msg_lower in ['шаблоны', 'какие бывают агенты']:
            return self._list_templates()

        # Статистика
        if msg_lower in ['статистика', 'статус', 'состояние системы']:
            return self._show_statistics()

        # Обновить реестр
        if msg_lower in ['обнови реестр', 'просканируй агентов']:
            return await self._scan_agents()

        # Запуск/остановка
        if msg_lower.startswith('запусти агента'):
            return await self._run_agent(message)
        if msg_lower.startswith('останови агента'):
            return await self._stop_agent(message)

        if msg_lower.startswith('проанализируй') or msg_lower.startswith('анализ'):
          return await self._analyze_agent(message)

        # Общий вопрос к нейросети
        return await self._call_ollama_with_prompt(message, user_name)

    async def _create_agent(self, message: str) -> str:
        """Создаёт нового агента"""
        description = message.replace('создай агента', '').replace('новый агент', '').strip()
        if not description:
            return "Опиши, какого агента создать."

        self.logger.info(f"🎨 Создание агента для: {description}")

        result = await agent_creator.create_new_agent(
            description, self.ollama_checked, self._call_ollama,
            self.logger, self.project_root, self.base_path
        )

        if isinstance(result, str):
            return result

        agent_id, design = result

        # Обновляем реестр
        await self._scan_agents()

        instructions = agent_creator.generate_setup_instructions(agent_id)

        return (f"✅ *Агент {agent_id} создан!*\n\n"
                f"📁 Файл: src/agents/{agent_id}/agent.py\n\n"
                f"{design}\n\n"
                f"{instructions}")

    async def _add_functionality(self, message: str) -> str:
        """Добавляет функционал агенту"""
        parts = message.lower()
        for word in ['добавь функционал', 'добавь команду']:
            parts = parts.replace(word, '')
        parts = parts.strip().split(' ', 1)

        if len(parts) < 2:
            return "Укажи агента и функционал."

        return await code_manager.add_functionality(
            parts[0].strip(), parts[1].strip(),
            self.agents_registry, self._call_ollama,
            self.logger, self.project_root
        )

    def _show_code(self, message: str) -> str:
        """Показывает код агента"""
        agent_name = message.lower()
        for word in ['покажи код', 'код агента', 'показать код']:
            agent_name = agent_name.replace(word, '')
        agent_name = agent_name.strip()

        if not agent_name:
            return "Укажи имя агента."

        return code_manager.show_code(agent_name, self.agents_registry, self.project_root)

    async def _update_agent(self, message: str) -> str:
        """Обновляет агента"""
        parts = message.lower()
        for word in ['обнови агента', 'измени агента']:
            parts = parts.replace(word, '')
        parts = parts.strip().split(' ', 1)

        if len(parts) < 2:
            return "Укажи агента и что изменить."

        return await code_manager.add_functionality(
            parts[0].strip(), parts[1].strip(),
            self.agents_registry, self._call_ollama,
            self.logger, self.project_root
        )

    async def _run_agent(self, message: str) -> str:
        """Запускает агента"""
        agent_name = message.lower().replace('запусти агента', '').replace('запустить агента', '').strip()
        return process_manager.run_agent(
            agent_name, self.agents_registry,
            self.project_root, self.running_agents
        )

    async def _stop_agent(self, message: str) -> str:
        """Останавливает агента"""
        agent_name = message.lower().replace('останови агента', '').replace('остановить агента', '').strip()
        return process_manager.stop_agent(
            agent_name, self.agents_registry, self.running_agents
        )

    def _list_agents(self) -> str:
        """Показывает список агентов"""
        agents = self.agents_registry.get('agents', {})
        if not agents:
            return "📭 Нет агентов"

        result = "📋 *Агенты:*\n\n"
        for aid, info in agents.items():
            status = "🟢" if aid in self.running_agents else "⚫"
            result += f"{status} *{info.get('name')}* (`{aid}`)\n"
            result += f"   {info.get('role')}\n"
        return result

    async def _get_agent_info(self, message: str) -> str:
        """Информация об агенте"""
        agent_name = message.lower().replace('агент', '').replace('кто такой', '').strip()

        for aid, info in self.agents_registry.get('agents', {}).items():
            if agent_name in aid or agent_name in info.get('name', '').lower():
                status = "🟢 Запущен" if aid in self.running_agents else "⚫ Остановлен"
                return (f"*{info.get('name')}* (`{aid}`)\n"
                       f"📌 {info.get('role')}\n"
                       f"📝 {info.get('description')}\n"
                       f"📁 {info.get('file')}\n"
                       f"🔄 {status}")

        return f"❌ Агент '{agent_name}' не найден"

    def _list_templates(self) -> str:
        """Показывает шаблоны"""
        result = "📚 *Шаблоны:*\n\n"
        for tid, tpl in self.templates.items():
            result += f"• *{tpl.get('name')}* — {tpl.get('description')}\n"
        return result

    def _show_statistics(self) -> str:
        """Показывает статистику"""
        agents = self.agents_registry.get('agents', {})
        return (f"📊 *Статистика:*\n\n"
               f"• Всего агентов: {len(agents)}\n"
               f"• Запущено: {len(self.running_agents)}")

    async def _scan_agents(self) -> str:
        """Сканирует агентов"""
        agents_path = Path(__file__).parent.parent
        found = []

        for d in agents_path.iterdir():
            if d.is_dir() and (d / 'agent.py').exists():
                found.append(d.name)

        # Обновляем реестр
        agents_dict = {}
        for aid in found:
            agents_dict[aid] = {
                'name': aid.capitalize(),
                'role': 'Автоопределён',
                'status': 'active',
                'description': 'Обнаружен при сканировании',
                'file': f'src/agents/{aid}/agent.py'
            }

        self.agents_registry['agents'] = agents_dict
        self.agents_registry['statistics']['last_updated'] = datetime.now().isoformat()
        core.save_registry(self.base_path, self.agents_registry)

        return f"✅ Найдено агентов: {len(found)}"

    async def _call_ollama_with_prompt(self, message: str, user_name: str) -> str:
        """Вызывает Ollama с промптом"""
        if not self.ollama_checked:
            return self._get_fallback_response(message)

        prompt = f"""Ты — Виктор, архитектор AI-систем. Ответь пользователю {user_name}: {message}"""
        return await self._call_ollama(prompt)

    def _get_fallback_response(self, message: str) -> str:
        """Заглушка без нейросети"""
        return ("Автономный режим. Команды: агенты, создать агента, показать код, запустить агента")

    def _get_welcome(self) -> str:
        return f"Здравствуйте, {self.user_name}. Я Виктор, архитектор."

    def _get_help(self) -> str:
        return ("*Команды:*\n"
                "• агенты — список\n"
                "• создать агента [описание]\n"
                "• показать код [агент]\n"
                "• запустить агента [имя]\n"
                "• остановить агента [имя]\n"
                "• статистика\n"
                "• шаблоны")

    async def _analyze_agent(self, message: str) -> str:
      """Анализирует код агента и предлагает улучшения"""
      agent_name = message.lower()
      for word in ['проанализируй', 'анализ', 'проанализировать']:
          agent_name = agent_name.replace(word, '')
      agent_name = agent_name.strip()

      if not agent_name:
          return "Укажи имя агента. Например: `проанализируй secretary`"

      self.logger.info(f"🔍 Запрос на анализ агента: {agent_name}")

      # Проверяем доступность Ollama
      if not self.ollama_checked:
          await self._check_ollama_connection()

      if not self.ollama_checked:
          return "🔌 Нейросеть не доступна. Не могу выполнить анализ."

      return await code_manager.analyze_agent(
          agent_name, self.agents_registry,
          self._call_ollama, self.logger, self.project_root
      )


def main():
    print("🚀 Запуск Виктора...")

    token = os.environ.get('ARCHITECT_TOKEN')
    if not token:
        token_file = Path.home() / 'ai-agents' / 'config' / 'tokens.env'
        if token_file.exists():
            with open(token_file, 'r') as f:
                for line in f:
                    if line.startswith('ARCHITECT_TOKEN='):
                        token = line.strip().split('=', 1)[1].strip()
                        break

    if not token:
        print("❌ Токен не найден!")
        return

    agent = ArchitectAgent()
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_message))

    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")

if __name__ == '__main__':
    main()
