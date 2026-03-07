import sys
import json
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.agent import BaseAgent

class WordStormCardAgent(BaseAgent):
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.display_name = "WordStormCard"

        # Путь к карточкам (в data/game_cards)
        self.cards_path = self.get_storage_path('game_cards')
        self.cards_path.mkdir(parents=True, exist_ok=True)

        # Загружаем ручные карточки
        self.manual_cards = self._load_cards('manual_cards.json')
        # Загружаем сгенерированные (если есть)
        self.generated_cards = self._load_cards('generated_cards.json')

        # Путь к Flutter-проекту (будет передан из конфига или переменной окружения)
        self.flutter_project_path = Path(self.config.get('flutter_project_path', '/mnt/d/prog/WordStorm'))

    def _load_cards(self, filename: str) -> List[Dict]:
        file_path = self.cards_path / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_cards(self, cards: List[Dict], filename: str):
        with open(self.cards_path / filename, 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)

    async def get_card(self, category: Optional[str] = None, language: str = "ru") -> Dict:
        """
        Возвращает карточку. Сначала ищет среди ручных, подходящих по категории.
        Если нет — можно будет генерировать через LLM.
        Сейчас просто возвращает первую попавшуюся или генерирует заглушку.
        """
        # Поиск по категории среди ручных
        if category:
            for card in self.manual_cards:
                if card.get('category') == category and card.get('language') == language:
                    return card

        # Если не нашли, пробуем среди сгенерированных
        if category:
            for card in self.generated_cards:
                if card.get('category') == category and card.get('language') == language:
                    return card

        # Если ничего нет, возвращаем заглушку (или вызываем LLM)
        new_card = {
            "id": f"card_{uuid.uuid4().hex[:6]}",
            "target": "Пример",
            "forbidden": ["слово1", "слово2", "слово3", "слово4", "слово5"],
            "category": category or "Общее",
            "language": language,
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "is_new": True
        }
        # Сохраним как сгенерированную
        self.generated_cards.append(new_card)
        self._save_cards(self.generated_cards, 'generated_cards.json')
        return new_card

    async def add_manual_cards(self, cards: List[Dict]):
        """Добавляет карточки вручную (из загруженного JSON)"""
        existing_ids = {c['id'] for c in self.manual_cards}
        new_cards = [c for c in cards if c['id'] not in existing_ids]
        self.manual_cards.extend(new_cards)
        self._save_cards(self.manual_cards, 'manual_cards.json')
        return len(new_cards)

    async def analyze_flutter_code(self) -> str:
        """Анализирует код Flutter-проекта (заглушка)"""
        # Позже здесь будет вызов LLM с кодом проекта
        return "Анализ кода Flutter пока не реализован"
