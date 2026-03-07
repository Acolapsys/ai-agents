#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import logging
import sys
import threading
import time
import schedule
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable

# Настраиваем корневой логгер ТОЛЬКО один раз
logging.basicConfig(
    level=logging.WARNING,  # По умолчанию только WARNING и выше
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Отключаем подробные логи от библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)  # Для telegram оставим INFO
logging.getLogger("schedule").setLevel(logging.WARNING)

class BaseAgent:
    """
    Базовый класс для всех агентов.
    Содержит общую функциональность: логирование, хранилища, планировщик, работу с данными пользователя.
    """

    def __init__(self, config_path: Optional[str] = None):
        print(f"🔵 BaseAgent.__init__: start for {self.__class__.__name__}")

        # Сохраняем config_path
        self.config_path = config_path

        # Загружаем конфигурацию
        self.config = self._load_config(config_path)

        # Базовые атрибуты
        self.name = self.config.get('name', self.__class__.__name__.lower())
        self.display_name = self.name.capitalize()

        # !!! ВАЖНО: сначала инициализируем базовые пути !!!
        self.base_path = Path.home() / 'ai-agents' / 'data'
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Настраиваем логирование для этого агента
        self._setup_logging()
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)  # Для нашего агента - INFO
        self.logger.info(f"🔵 Логирование настроено для {self.display_name}")

        # Теперь загружаем данные пользователя (уже можно использовать base_path)
        self.user_data = self._load_user_data()
        self.user_name = self.user_data.get('profile', {}).get('name', 'Пользователь')
        self.logger.info(f"📊 Данные пользователя загружены для {self.user_name}")

        # Планировщик (будет запущен при необходимости)
        self.scheduler_running = False
        self.scheduler_thread = None

        self.logger.info(f"✅ BaseAgent инициализирован для {self.display_name}")
        print(f"🔵 BaseAgent.__init__: end for {self.__class__.__name__}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Загружает конфигурацию агента"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}

    def _setup_logging(self):
        """Настраивает логирование для агента"""
        log_dir = Path.home() / 'ai-agents' / 'logs' / self.name
        log_dir.mkdir(parents=True, exist_ok=True)

        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Хендлер для файла - пишем всё от INFO и выше
        file_handler = logging.FileHandler(log_dir / 'agent.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Хендлер для консоли - только INFO и выше
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Получаем логгер для этого агента
        agent_logger = logging.getLogger(self.name)
        agent_logger.setLevel(logging.INFO)
        agent_logger.addHandler(file_handler)
        agent_logger.addHandler(console_handler)
        agent_logger.propagate = False  # Не передавать в корневой логгер

    def _load_user_data(self) -> Dict[str, Any]:
        """Загружает все данные о пользователе"""
        user_data = {}

        try:
            # Загружаем базовый профиль
            profile_path = self.base_path / 'user' / 'profile.yaml'
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    user_data['profile'] = yaml.safe_load(f) or {}
                    self.logger.info(f"📄 Профиль загружен из {profile_path}")

            # Загружаем данные о здоровье
            health_path = self.base_path / 'health' / 'profile.yaml'
            if health_path.exists():
                with open(health_path, 'r', encoding='utf-8') as f:
                    user_data['health'] = yaml.safe_load(f) or {}
                    self.logger.info(f"🏥 Данные о здоровье загружены")

            # Загружаем семейные данные
            family_path = self.base_path / 'family' / 'members.yaml'
            if family_path.exists():
                with open(family_path, 'r', encoding='utf-8') as f:
                    user_data['family'] = yaml.safe_load(f) or {}
                    self.logger.info(f"👨‍👩‍👧‍👦 Семейные данные загружены")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных пользователя: {e}")

        return user_data

    def start_scheduler(self, check_function: Callable, interval_minutes: int = 1):
        """
        Запускает планировщик для периодических задач

        Args:
            check_function: функция для периодического вызова
            interval_minutes: интервал в минутах
        """
        if self.scheduler_running:
            self.logger.warning("Планировщик уже запущен")
            return

        def run_scheduler():
            schedule.every(interval_minutes).minutes.do(check_function)
            self.scheduler_running = True
            self.logger.info(f"⏰ Планировщик запущен с интервалом {interval_minutes} мин")

            while self.scheduler_running:
                try:
                    schedule.run_pending()
                    time.sleep(10)
                except Exception as e:
                    self.logger.error(f"Ошибка в планировщике: {e}")
                    time.sleep(60)

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("🔄 Планировщик запущен в фоновом потоке")

    def stop_scheduler(self):
        """Останавливает планировщик"""
        self.scheduler_running = False
        self.logger.info("⏹️ Планировщик остановлен")

    def get_storage_path(self, *paths: str) -> Path:
        """Возвращает путь к папке хранения"""
        return self.base_path.joinpath(*paths)

    def save_yaml(self, data: Any, *paths: str):
        """Сохраняет данные в YAML файл"""
        file_path = self.get_storage_path(*paths)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        self.logger.info(f"💾 Сохранено в {file_path}")

    def load_yaml(self, *paths: str, default: Any = None) -> Any:
        """Загружает данные из YAML файла"""
        file_path = self.get_storage_path(*paths)

        if not file_path.exists():
            return default if default is not None else {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки {file_path}: {e}")
            return default if default is not None else {}

    def append_text(self, text: str, *paths: str):
        """Добавляет текст в файл"""
        file_path = self.get_storage_path(*paths)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(text)

        self.logger.info(f"📝 Текст добавлен в {file_path}")

    def read_text(self, *paths: str) -> str:
        """Читает текст из файла"""
        file_path = self.get_storage_path(*paths)

        if not file_path.exists():
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка чтения {file_path}: {e}")
            return ""

    async def call_ollama(self, prompt: str, model: str = "qwen2.5:7b") -> str:
        """
        Вызывает Ollama для обработки запроса

        Args:
            prompt: промпт для отправки
            model: модель для использования

        Returns:
            ответ от модели
        """
        import aiohttp

        self.logger.info(f"🤖 Вызов Ollama (модель: {model})")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': model,
                        'prompt': prompt,
                        'stream': False
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get('response', '')
                        self.logger.info(f"✅ Ответ получен ({len(answer)} символов)")
                        return answer
                    else:
                        self.logger.error(f"Ошибка Ollama: статус {response.status}")
                        return f"⚠️ Ошибка связи с нейросетью (код {response.status})"

        except aiohttp.ClientConnectorError:
            self.logger.error("❌ Ollama не запущена!")
            return "⚠️ Нейросеть не запущена. Запустите Ollama командой 'ollama serve'"
        except asyncio.TimeoutError:
            self.logger.error("⏰ Таймаут при обращении к Ollama")
            return "⚠️ Превышено время ожидания ответа от нейросети"
        except Exception as e:
            self.logger.error(f"❌ Ошибка при вызове Ollama: {e}")
            return f"⚠️ Ошибка: {e}"

    def build_prompt(self, message: str, context: Optional[str] = None) -> str:
        """
        Базовый метод построения промпта для LLM
        Должен быть переопределён в дочерних классах
        """
        return f"User: {message}"

    def get_current_time(self) -> str:
        """Возвращает текущее время в формате ЧЧ:ММ"""
        return datetime.now().strftime("%H:%M")

    def get_current_date(self) -> str:
        """Возвращает текущую дату в формате ГГГГ-ММ-ДД"""
        return datetime.now().strftime("%Y-%m-%d")

    def get_current_datetime_str(self) -> str:
        """Возвращает текущую дату и время"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
