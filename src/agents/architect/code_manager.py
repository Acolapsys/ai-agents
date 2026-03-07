# -*- coding: utf-8 -*-
"""
Модуль для работы с кодом агентов.
"""

import shutil
from pathlib import Path
from typing import Dict, Any

import agents.architect.utils as utils

async def add_functionality(agent_name: str, functionality: str, registry: Dict[str, Any],
                           call_ollama_func, logger, project_root: Path) -> str:
    """
    Добавляет новый функционал существующему агенту.
    """
    # Находим агента
    agent_file = None
    agent_display_name = None
    agent_id = None

    logger.info(f"🔍 Поиск агента '{agent_name}' для добавления функционала")

    for aid, info in registry.get('agents', {}).items():
        if (agent_name in aid or
            agent_name in info.get('name', '').lower() or
            agent_name in info.get('role', '').lower()):
            agent_file = project_root / info.get('file', '')
            agent_display_name = info.get('name', aid)
            agent_id = aid
            logger.info(f"✅ Найден агент: {agent_display_name}")
            break

    if not agent_file or not agent_file.exists():
        logger.error(f"❌ Агент '{agent_name}' не найден")
        return f"❌ Агент '{agent_name}' не найден."

    # Читаем текущий код
    logger.info(f"📖 Чтение текущего кода")
    with open(agent_file, 'r', encoding='utf-8') as f:
        current_code = f.read()

    # Формируем промпт
    prompt_lines = [
        "Ты — Виктор, опытный Python-разработчик. Добавь новый функционал в существующего агента.",
        "",
        "Текущий код агента:",
        "```python",
        current_code,
        "```",
        "",
        f"Новый функционал для добавления: {functionality}",
        "",
        "Требования:",
        "1. Сохрани все существующие функции и методы",
        "2. Добавь новый функционал, сохраняя стиль кода",
        "3. Добавь обработку новых команд в _process_request",
        "4. Добавь необходимые вспомогательные методы",
        "5. Сохрани все импорты",
        "6. Добавь логирование новых действий",
        "7. Комментарии на русском языке",
        "",
        "Сгенерируй ПОЛНЫЙ обновлённый код агента.",
        "Верни ТОЛЬКО код, без пояснений и markdown-форматирования."
    ]

    prompt = "\n".join(prompt_lines)

    logger.info(f"🤖 Отправка запроса в Ollama")
    new_code = await call_ollama_func(prompt)
    new_code = utils.clean_code(new_code)

    # Создаём бэкап
    backup_file = agent_file.with_suffix('.py.bak')
    shutil.copy2(agent_file, backup_file)
    logger.info(f"📦 Бэкап сохранён")

    # Сохраняем новый код
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(new_code)
    logger.info(f"💾 Новый код сохранён")

    return (f"✅ *Функционал добавлен к агенту {agent_display_name}*\n\n"
            f"📁 Файл обновлён: {agent_file}\n"
            f"📦 Бэкап сохранён: {backup_file}\n\n"
            f"Перезапусти агента: `останови агента {agent_id}` и `запусти агента {agent_id}`")

def show_code(agent_name: str, registry: Dict[str, Any], project_root: Path) -> str:
    """Показывает код агента"""
    # Находим агента
    agent_file = None
    agent_display_name = None

    for aid, info in registry.get('agents', {}).items():
        if (agent_name in aid or
            agent_name in info.get('name', '').lower() or
            agent_name in info.get('role', '').lower()):
            agent_file = project_root / info.get('file', '')
            agent_display_name = info.get('name', aid)
            break

    if not agent_file or not agent_file.exists():
        return f"❌ Агент '{agent_name}' не найден."

    # Читаем код
    with open(agent_file, 'r', encoding='utf-8') as f:
        code = f.read()

    # Возвращаем код
    if len(code) > 3500:
        return (f"📄 *Код агента {agent_display_name} (первые 3500 символов):*\n\n"
               f"```python\n{code[:3500]}...\n```\n\n"
               f"*Полный код можно посмотреть в файле:* `{agent_file}`")
    else:
        return f"📄 *Код агента {agent_display_name}:*\n\n```python\n{code}\n```"


async def analyze_agent(agent_name: str, registry: Dict[str, Any],
                       call_ollama_func, logger, project_root: Path) -> str:
    """Анализирует код агента и предлагает улучшения"""
    # Находим агента
    agent_file = None
    agent_display_name = None

    logger.info(f"🔍 Поиск агента '{agent_name}' для анализа")

    for aid, info in registry.get('agents', {}).items():
        if (agent_name in aid or
            agent_name in info.get('name', '').lower() or
            agent_name in info.get('role', '').lower()):
            agent_file = project_root / info.get('file', '')
            agent_display_name = info.get('name', aid)
            logger.info(f"✅ Найден агент: {agent_display_name}")
            break

    if not agent_file or not agent_file.exists():
        logger.error(f"❌ Агент '{agent_name}' не найден")
        return f"❌ Агент '{agent_name}' не найден."

    # Читаем код
    logger.info(f"📖 Чтение кода агента {agent_display_name}")
    with open(agent_file, 'r', encoding='utf-8') as f:
        code = f.read()

    logger.info(f"✅ Код прочитан, длина: {len(code)} символов")

    # Формируем промпт для анализа
    prompt_lines = [
        "Ты — Виктор, опытный архитектор AI-систем. Проанализируй код агента и предложи 3 конкретных улучшения.",
        "",
        "Код агента:",
        "```python",
        code,
        "```",
        "",
        "Предложи 3 улучшения, которые:",
        "1. Улучшат производительность",
        "2. Добавят полезный функционал",
        "3. Сделают код чище и поддерживаемее",
        "",
        "Для каждого улучшения объясни:",
        "- Что именно изменить",
        "- Почему это полезно",
        "- Как это реализовать (с примером кода если нужно)",
        "",
        "Ответ оформи структурированно, с эмодзи для наглядности."
    ]

    prompt = "\n".join(prompt_lines)

    logger.info(f"🤖 Отправка запроса в Ollama для анализа")
    analysis = await call_ollama_func(prompt)

    return analysis