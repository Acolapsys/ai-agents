import subprocess
import psutil
import signal
from pathlib import Path
from typing import Dict, Optional
import yaml
import os
import time

from .config import Config
from .models import AgentInfo

class ProcessManager:
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self._load_agents()

    def _load_agents(self):
        """Загружает список агентов из конфига или реестра архитектора"""
        # Вариант 1: читать из YAML (пока упростим)
        config_file = Config.AGENTS_CONFIG
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                for agent_id, info in data.get('agents', {}).items():
                    self.agents[agent_id] = AgentInfo(
                        id=agent_id,
                        name=info.get('name', agent_id),
                        description=info.get('description', ''),
                        run_script=info.get('run_script', f"{agent_id}/run.sh"),
                        status='stopped',
                        port=info.get('port'),
                    )
        else:
            # Заглушка для теста
            self.agents = {
                'designer': AgentInfo(id='designer', name='Дизайнер', run_script='designer/run.sh'),
                'mentor': AgentInfo(id='mentor', name='Ментор', run_script='mentor/run.sh'),
                'secretary': AgentInfo(id='secretary', name='Секретарь', run_script='secretary/run.sh'),
                'family': AgentInfo(id='family', name='Семейный советник', run_script='family/run.sh'),
                'architect': AgentInfo(id='architect', name='Архитектор', run_script='architect/run.sh'),
                'english_mentor': AgentInfo(id='english_mentor', name='Учитель английского', run_script='english_mentor/run.sh'),
            }

    def _get_script_path(self, agent_id: str) -> Path:
        return Config.AGENTS_ROOT / agent_id / "run.sh"

    def get_status(self, agent_id: str) -> str:
        agent = self.agents.get(agent_id)
        if not agent:
            return "unknown"
        if agent.pid and psutil.pid_exists(agent.pid):
            return "running"
        return "stopped"

    def start_agent(self, agent_id: str) -> bool:
        script = self._get_script_path(agent_id)
        if not script.exists():
            return False
        try:
            # Запускаем скрипт в фоне
            proc = subprocess.Popen(
                [str(script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self.agents[agent_id].pid = proc.pid
            return True
        except Exception:
            return False

    def stop_agent(self, agent_id: str) -> bool:
          agent = self.agents.get(agent_id)
          if not agent or not agent.pid:
              return False
          try:
              # Получаем ID группы процессов (session)
              pgid = os.getpgid(agent.pid)
              # Отправляем SIGTERM всей группе
              os.killpg(pgid, signal.SIGTERM)

              # Даём время на завершение
              time.sleep(2)

              # Проверяем, жив ли процесс
              try:
                  proc = psutil.Process(agent.pid)
                  if proc.is_running():
                      # Если ещё жив, отправляем SIGKILL всей группе
                      os.killpg(pgid, signal.SIGKILL)
                      time.sleep(1)
              except psutil.NoSuchProcess:
                  pass

              agent.pid = None
              return True

          except ProcessLookupError:
              # Группа уже не существует (процессы завершились)
              agent.pid = None
              return True
          except Exception as e:
              print(f"Error stopping agent {agent_id}: {e}")
              return False

    def restart_agent(self, agent_id: str) -> bool:
        self.stop_agent(agent_id)
        # небольшая пауза, чтобы порт освободился
        import time
        time.sleep(1)
        return self.start_agent(agent_id)

    def list_agents(self) -> Dict[str, AgentInfo]:
        # обновляем статусы перед отправкой
        for aid, agent in self.agents.items():
            agent.status = self.get_status(aid)
        return self.agents

    def get_agent_log_path(self, agent_id: str) -> Path:
        """Возвращает путь к файлу лога агента."""
        # Основной путь: данные агента (совпадает с BaseAgent._setup_logging)
        logs_log = Path.home() / "ai-agents" / "logs" / agent_id / "agent.log"
        if logs_log.exists():
            return logs_log
        # # Запасные пути для обратной совместимости
        # data_log = Path.home() / "ai-agents" / "data" / agent_id / "agent.log"
        # if data_log.exists():
        #     return data_log
        # service_log = Config.AGENTS_ROOT / agent_id / "agent.log"
        # if service_log.exists():
        #     return service_log
        return None

    def read_agent_log(self, agent_id: str, limit: int = 50, offset: int = 0) -> dict:
        """
        Читает последние строки из файла лога агента.
        Возвращает словарь с полями:
        - success: bool
        - lines: список строк (последние lines)
        - total: общее количество строк (если нужно)
        - error: сообщение об ошибке (если success=False)
        """
        log_path = self.get_agent_log_path(agent_id)
        if not log_path:
            return {"success": False, "error": "Log file not found"}
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            total = len(all_lines)
            start = max(0, total - limit - offset)
            end = total - offset
            selected_lines = all_lines[start:end]
            return {
                "success": True,
                "lines": selected_lines,
                "total": total,
                "filename": str(log_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}