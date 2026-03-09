import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class EnglishMentorAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "Виктор Иванович Лингвист"

        # Пути к данным
        self.profile_path = self.agent_data_path / "profile.json"
        self.vocab_path = self.agent_data_path / "vocabulary.json"
        self.lessons_path = self.agent_data_path / "lessons.json"

        # Загружаем или создаём данные
        self.profile = self._load_profile()
        self.vocabulary = self._load_vocabulary()
        self.lessons = self._load_lessons()
        self.current_lesson = None  # id текущего урока

    # --- Вспомогательные методы для работы с файлами ---
    def _load_profile(self) -> Dict:
        if self.profile_path.exists():
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Профиль по умолчанию
        return {
            "level": "beginner",
            "goal": "Разговорный английский для работы",
            "strengths": [],
            "weaknesses": [],
            "total_lessons": 0,
            "total_time": 0,
            "last_lesson": None
        }

    def _save_profile(self):
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def _load_vocabulary(self) -> List[str]:
        if self.vocab_path.exists():
            with open(self.vocab_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_vocabulary(self):
        with open(self.vocab_path, 'w', encoding='utf-8') as f:
            json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)

    def _load_lessons(self) -> List[Dict]:
        if self.lessons_path.exists():
            with open(self.lessons_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_lessons(self):
        with open(self.lessons_path, 'w', encoding='utf-8') as f:
            json.dump(self.lessons, f, ensure_ascii=False, indent=2)

    # --- Инструменты ---
    async def get_profile(self) -> str:
        """Возвращает профиль ученика в JSON."""
        return json.dumps(self.profile, ensure_ascii=False)

    async def get_vocabulary(self) -> str:
        """Возвращает список слов в JSON."""
        return json.dumps(self.vocabulary, ensure_ascii=False)

    async def add_word(self, word: str) -> str:
        """Добавляет слово в словарь."""
        word = word.strip().lower()
        if not word:
            return json.dumps({"error": "Слово не может быть пустым"})
        if word in self.vocabulary:
            return json.dumps({"error": f"Слово '{word}' уже есть в словаре"})
        self.vocabulary.append(word)
        self._save_vocabulary()
        return json.dumps({"status": "ok", "message": f"Слово '{word}' добавлено"})

    async def start_lesson(self, topic: str = "general") -> str:
        """Начинает новый урок."""
        lesson_id = datetime.now().isoformat()
        lesson = {
            "id": lesson_id,
            "topic": topic,
            "started_at": lesson_id,
            "messages": [],
            "new_words": []
        }
        self.lessons.append(lesson)
        self.current_lesson = lesson
        self._save_lessons()
        return json.dumps({
            "status": "ok",
            "lesson_id": lesson_id,
            "topic": topic,
            "message": f"Урок по теме '{topic}' начат"
        })

    async def continue_lesson(self, user_message: str) -> str:
        """Сохраняет сообщение ученика в текущий урок."""
        if not self.current_lesson:
            return json.dumps({"error": "Нет активного урока. Начните урок командой 'урок'."})
        self.current_lesson["messages"].append({
            "time": datetime.now().isoformat(),
            "user": user_message
        })
        # Обновляем в общем списке
        for i, l in enumerate(self.lessons):
            if l["id"] == self.current_lesson["id"]:
                self.lessons[i] = self.current_lesson
                break
        self._save_lessons()
        return json.dumps({"status": "ok"})

    async def end_lesson(self) -> str:
        """Завершает текущий урок и возвращает статистику."""
        if not self.current_lesson:
            return json.dumps({"error": "Нет активного урока."})
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_lesson["started_at"])
        duration = int((end_time - start_time).total_seconds() // 60)
        self.current_lesson["ended_at"] = end_time.isoformat()
        self.current_lesson["duration"] = duration
        # Обновляем профиль
        self.profile["total_lessons"] += 1
        self.profile["total_time"] += duration
        self.profile["last_lesson"] = end_time.isoformat()
        self._save_profile()
        # Обновляем в lessons
        for i, l in enumerate(self.lessons):
            if l["id"] == self.current_lesson["id"]:
                self.lessons[i] = self.current_lesson
                break
        self._save_lessons()
        result = {
            "status": "ok",
            "duration": duration,
            "new_words": len(self.current_lesson.get("new_words", [])),
            "total_lessons": self.profile["total_lessons"]
        }
        self.current_lesson = None
        return json.dumps(result, ensure_ascii=False)