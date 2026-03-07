# -*- coding: utf-8 -*-
import re
import yaml
import aiohttp
from pathlib import Path
from typing import Dict, Any, Tuple

# Импортируем через абсолютный путь
import agents.architect.utils as utils
import agents.architect.core_utils as core_utils

async def create_new_agent(description: str, ollama_checked: bool, call_ollama_func, logger, project_root, storage_path) -> Tuple[str, str]:
    """Создаёт нового агента с генерацией кода"""
    if not ollama_checked:
        return None, "🔌 Нейросеть не доступна. Не могу сгенерировать код."
    
    # Генерируем дизайн агента
    design_prompt = f"""Ты — Виктор, опытный архитектор AI-систем. Спроектируй нового AI-агента для задачи: "{description}"

Сгенерируй ПОЛНЫЙ дизайн агента с:

1. **agent_id**: короткое уникальное имя (например, finance_helper, travel_planner)
2. **display_name**: имя для отображения по-русски
3. **role**: краткое описание роли
4. **personality**: 3-4 черты характера, возраст, история
5. **voice_tone**: как говорит
6. **features**: список основных функций
7. **commands**: список команд, которые должен понимать агент
8. **storage**: какие данные нужно хранить

Оформи ответ с четкими секциями на русском языке."""
    
    design_response = await call_ollama_func(design_prompt)
    
    # Извлекаем agent_id
    agent_id_match = re.search(r'\*\*agent_id\*\*:?\s*(\w+)', design_response, re.IGNORECASE)
    agent_id = agent_id_match.group(1) if agent_id_match else utils.generate_agent_id(description)
    
    # Генерируем код
    code_prompt = f"""Ты — Виктор, опытный Python-разработчик. Сгенерируй полный код Telegram-бота на основе этого дизайна:

{design_response}

Агент должен:
- Наследоваться от BaseAgent (уже есть в core/agent.py)
- Использовать async/await
- Иметь правильную обработку ошибок
- Хранить данные в self.get_storage_path()
- Включать все описанные функции
- Комментарии и логирование на русском

Сгенерируй ПОЛНЫЙ Python-код агента. Включи:
- Все импорты
- Определение класса
- Метод __init__
- Все необходимые методы
- Правильное логирование

Код должен быть готов к немедленному запуску. НЕ ИСПОЛЬЗУЙ markdown-форматирование в ответе, только чистый код."""
    
    code = await call_ollama_func(code_prompt)
    code = utils.clean_code(code)
    
    # Сохраняем файлы
    agent_dir = project_root / 'src' / 'agents' / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    agent_file = agent_dir / 'agent.py'
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    init_file = agent_dir / '__init__.py'
    init_file.touch()
    
    # Добавляем личность
    await add_personality(agent_id, design_response, project_root)
    
    return agent_id, design_response

async def add_personality(agent_id: str, design: str, project_root: Path):
    """Добавляет личность агента в конфиг"""
    personalities_file = project_root / 'config' / 'personalities.yaml'
    
    # Извлекаем данные
    name_match = re.search(r'\*\*display_name\*\*:?\s*([^\n]+)', design)
    name = name_match.group(1).strip() if name_match else agent_id.capitalize()
    
    traits_match = re.search(r'\*\*personality\*\*:?\s*([^\n]+)', design, re.IGNORECASE)
    traits = traits_match.group(1).strip() if traits_match else 'дружелюбный, полезный'
    
    role_match = re.search(r'\*\*role\*\*:?\s*([^\n]+)', design, re.IGNORECASE)
    role = role_match.group(1).strip() if role_match else 'Помощник'
    
    # Загружаем существующий файл
    if personalities_file.exists():
        with open(personalities_file, 'r', encoding='utf-8') as f:
            personalities = yaml.safe_load(f) or {}
    else:
        personalities = {}
    
    # Добавляем новую личность
    personalities[agent_id] = {
        'name': name,
        'role': role,
        'traits': [t.strip() for t in traits.split(',')] if isinstance(traits, str) else [traits],
        'background': 'Создан архитектором Виктором'
    }
    
    # Сохраняем
    with open(personalities_file, 'w', encoding='utf-8') as f:
        yaml.dump(personalities, f, allow_unicode=True, sort_keys=False)

def generate_setup_instructions(agent_id: str) -> str:
    """Генерирует инструкцию по запуску агента"""
    return (f"📋 *Как запустить агента:*\n\n"
            f"1. Создай бота у @BotFather и получи токен\n"
            f"2. Добавь токен в config/tokens.env:\n"
            f"   `{agent_id.upper()}_TOKEN=твой_токен`\n\n"
            f"3. Создай скрипт запуска run_{agent_id}.sh:\n"
            f"```bash\n"
            f"#!/bin/bash\n"
            f"cd ~/ai-agents\n"
            f"source venv/bin/activate\n"
            f"cd src/agents/{agent_id}\n"
            f"python agent.py\n"
            f"```\n\n"
            f"4. Запусти: `chmod +x run_{agent_id}.sh && ./run_{agent_id}.sh`")
