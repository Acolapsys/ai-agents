# -*- coding: utf-8 -*-
import re
from pathlib import Path

def clean_code(code: str) -> str:
    """Очищает код от markdown-форматирования"""
    code = re.sub(r'^```python\s*', '', code, flags=re.MULTILINE)
    code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'```\s*$', '', code, flags=re.MULTILINE)
    return code.strip()

def generate_agent_id(description: str) -> str:
    """Генерирует ID агента из описания"""
    words = description.lower().split()[:2]
    return '_'.join(words).replace('-', '_').replace(' ', '_').replace('ё', 'e')

def get_project_root() -> Path:
    """Возвращает корневую папку проекта"""
    return Path.home() / 'ai-agents'