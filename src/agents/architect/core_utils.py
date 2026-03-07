# -*- coding: utf-8 -*-
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def load_agents_registry(storage_path: Path) -> Dict[str, Any]:
    """Загружает или создаёт реестр агентов"""
    registry_file = storage_path / 'registry' / 'agents.yaml'

    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    # Создаём начальный реестр
    initial_registry = {
        'agents': {
            'secretary': {
                'name': 'Михаил',
                'role': 'Личный секретарь',
                'status': 'active',
                'description': 'Заметки, список покупок, задачи, напоминания',
                'created': datetime.now().isoformat(),
                'file': 'src/agents/secretary/agent.py'
            },
            'architect': {
                'name': 'Виктор',
                'role': 'Главный архитектор',
                'status': 'active',
                'description': 'Управление системой агентов, проектирование и код',
                'created': datetime.now().isoformat(),
                'file': 'src/agents/architect/agent.py'
            },
            'english_mentor': {
                'name': 'Виктор Иванович Лингвист',
                'role': 'Учитель английского',
                'status': 'active',
                'description': 'Персональный учитель английского с отслеживанием прогресса',
                'created': datetime.now().isoformat(),
                'file': 'src/agents/english_mentor/agent.py'
            }
        },
        'statistics': {
            'total_agents': 3,
            'active_agents': 3,
            'last_updated': datetime.now().isoformat()
        }
    }

    registry_file.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(initial_registry, f, allow_unicode=True, sort_keys=False)

    return initial_registry

def load_templates(storage_path: Path) -> Dict[str, Any]:
    """Загружает или создаёт шаблоны агентов"""
    templates_file = storage_path / 'registry' / 'templates.yaml'

    if templates_file.exists():
        with open(templates_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    templates = {
        'assistant': {
            'name': 'Новый ассистент',
            'role': 'Помощник',
            'description': 'Базовый шаблон ассистента',
            'personality': {'traits': ['полезный', 'дружелюбный'], 'voice_tone': 'дружелюбно'},
            'tools': ['notes', 'tasks']
        },
        'expert': {
            'name': 'Эксперт',
            'role': 'Эксперт в области',
            'description': 'Шаблон эксперта со знаниями в конкретной области',
            'personality': {'traits': ['знающий', 'терпеливый'], 'voice_tone': 'обстоятельно'},
            'tools': ['knowledge_base', 'search']
        },
        'mentor': {
            'name': 'Наставник',
            'role': 'Ментор',
            'description': 'Шаблон для обучения и менторства',
            'personality': {'traits': ['мудрый', 'наставляющий'], 'voice_tone': 'спокойно, с вопросами'},
            'tools': ['code_review', 'explain']
        }
    }

    templates_file.parent.mkdir(parents=True, exist_ok=True)
    with open(templates_file, 'w', encoding='utf-8') as f:
        yaml.dump(templates, f, allow_unicode=True, sort_keys=False)

    return templates

def save_registry(storage_path: Path, registry: Dict[str, Any]):
    """Сохраняет реестр агентов"""
    registry_file = storage_path / 'registry' / 'agents.yaml'
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, allow_unicode=True, sort_keys=False)