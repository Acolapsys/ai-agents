import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class MentorAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "Ментор"

    # --- Инструменты ---
    async def explain_concept(self, concept: str) -> str:
        """Возвращает объяснение концепции. (Заглушка, позже можно вызывать модель)"""
        # Здесь можно было бы вызвать модель, но для простоты вернём заглушку.
        # В реальности модель сама сгенерирует ответ, но этот инструмент может быть полезен,
        # если нужно дополнительно получить данные из базы знаний.
        # Пока просто вернём JSON, который модель сможет использовать.
        return json.dumps({
            "status": "ok",
            "message": f"Объяснение концепции '{concept}' будет сгенерировано моделью.",
            "concept": concept
        })

    async def review_code(self, code: str) -> str:
        """Возвращает ревью кода (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Ревью кода (длина {len(code)} символов) будет выполнено моделью."
        })

    async def suggest_improvements(self, code: str) -> str:
        """Возвращает предложения по улучшению кода (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Предложения по улучшению кода (длина {len(code)} символов) будут сгенерированы моделью."
        })

    async def generate_example(self, task: str) -> str:
        """Возвращает пример кода по задаче (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Пример кода для задачи '{task}' будет сгенерирован моделью."
        })

    async def answer_question(self, question: str) -> str:
        """Возвращает ответ на вопрос (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Ответ на вопрос '{question}' будет сгенерирован моделью."
        })