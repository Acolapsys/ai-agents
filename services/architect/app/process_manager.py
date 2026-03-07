# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

def run_agent(agent_name: str, registry: Dict[str, Any], project_root: Path, 
             running_agents: Dict[str, subprocess.Popen]) -> str:
    """Запускает агента в отдельном процессе"""
    # Находим агента
    agent_info = None
    agent_id = None
    
    for aid, info in registry.get('agents', {}).items():
        if (agent_name in aid or 
            agent_name in info.get('name', '').lower() or
            agent_name in info.get('role', '').lower()):
            agent_info = info
            agent_id = aid
            break
    
    if not agent_info:
        return f"❌ Агент '{agent_name}' не найден."
    
    # Проверяем токен
    token_name = f"{agent_id.upper()}_TOKEN"
    token = os.environ.get(token_name)
    
    if not token:
        token_file = project_root / 'config' / 'tokens.env'
        if token_file.exists():
            with open(token_file, 'r') as f:
                for line in f:
                    if line.startswith(f'{token_name}='):
                        token = line.strip().split('=', 1)[1].strip()
                        break
    
    if not token:
        return (f"❌ Токен для агента {agent_info.get('name')} не найден.\n"
               f"Добавь `{token_name}=твой_токен` в config/tokens.env")
    
    # Запускаем процесс
    agent_script = project_root / agent_info.get('file', '')
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(agent_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, token_name: token}
        )
        running_agents[agent_id] = process
        return f"✅ Агент {agent_info.get('name')} запущен (PID: {process.pid})"
    except Exception as e:
        return f"❌ Ошибка запуска: {e}"

def stop_agent(agent_name: str, registry: Dict[str, Any], 
              running_agents: Dict[str, subprocess.Popen]) -> str:
    """Останавливает запущенного агента"""
    # Находим агента
    agent_id = None
    agent_info = None
    
    for aid, info in registry.get('agents', {}).items():
        if (agent_name in aid or 
            agent_name in info.get('name', '').lower() or
            agent_name in info.get('role', '').lower()):
            agent_info = info
            agent_id = aid
            break
    
    if not agent_info:
        return f"❌ Агент '{agent_name}' не найден."
    
    if agent_id not in running_agents:
        return f"Агент {agent_info.get('name')} не запущен"
    
    process = running_agents[agent_id]
    process.terminate()
    process.wait(timeout=5)
    del running_agents[agent_id]
    
    return f"✅ Агент {agent_info.get('name')} остановлен"
