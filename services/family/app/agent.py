import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class FamilyAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "Елена"

        self.family_data = self._load_family_data()
        self.events_history = self._load_events_history()

    # --- Вспомогательные методы для работы с данными ---
    def _load_family_data(self) -> Dict[str, Any]:
        family_file = self.agent_data_path / "members.yaml"
        if family_file.exists():
            with open(family_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {"members": [], "events": []}

    def _load_events_history(self) -> List[Dict]:
        events_file = self.agent_data_path / "events.json"
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_event(self, event: Dict):
        self.events_history.append(event)
        if len(self.events_history) > 100:
            self.events_history = self.events_history[-100:]
        events_file = self.agent_data_path / "events.json"
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(self.events_history, f, ensure_ascii=False, indent=2)

    def _find_person(self, query: str) -> Optional[Dict]:
        query = query.lower().strip()
        members = self.family_data.get('members', [])
        # Сначала по id
        for person in members:
            if person.get('id') == query:
                return person
        # Потом по имени
        for person in members:
            if query in person.get('name', '').lower():
                return person
            if query in person.get('preferred_name', '').lower():
                return person
        return None

    def _get_upcoming_birthdays(self, days: int = 30) -> List[Dict]:
        """Возвращает список ближайших дней рождения."""
        today = datetime.now()
        upcoming = []
        people = []
        spouse = self.family_data.get('spouse', {})
        if spouse and 'birthday' in spouse:
            people.append(('spouse', spouse))
        for child in self.family_data.get('children', []):
            if 'birthday' in child:
                people.append(('child', child))
        for rel_name, rel_data in self.family_data.get('parents', {}).items():
            if 'birthday' in rel_data:
                people.append(('relative', rel_data))
        for rel_type, person in people:
            try:
                bd_str = person['birthday']
                parts = bd_str.split('.')
                day = int(parts[0])
                month = int(parts[1])
                bd_this_year = datetime(today.year, month, day)
                if bd_this_year < today:
                    bd_this_year = datetime(today.year + 1, month, day)
                days_until = (bd_this_year - today).days
                if days_until <= days:
                    upcoming.append({
                        'name': person.get('name', 'родственник'),
                        'date': bd_this_year.strftime("%d.%m"),
                        'days': days_until,
                        'person_data': person
                    })
            except Exception:
                continue
        upcoming.sort(key=lambda x: x['days'])
        return upcoming

    # --- Инструменты ---
    async def get_family_members(self) -> str:
        """Возвращает информацию о всех членах семьи в формате JSON."""
        members = self.family_data.get('members', [])
        if not members:
            return json.dumps({"error": "Семейные данные не загружены или пусты"})

        result = {
            "members": []
        }
        for person in members:
            result["members"].append({
                "id": person.get('id'),
                "name": person.get('name'),
                "preferred_name": person.get('preferred_name'),
                "relation": person.get('relation'),
                "birthday": person.get('birthday'),
                "interests": person.get('interests', []),
                "preferences": person.get('preferences', {}),
                "deceased": person.get('deceased', False)
            })
        return json.dumps(result, ensure_ascii=False)

    async def get_person_info(self, name: str) -> str:
        """Возвращает информацию о человеке по имени или отношению в JSON формате."""
        person = self._find_person(name)
        if not person:
            return json.dumps({"error": f"Информация о {name} не найдена"})
        info = {
            "id": person.get('id'),
            "name": person.get('name'),
            "preferred_name": person.get('preferred_name'),
            "relation": person.get('relation'),
            "birthday": person.get('birthday'),
            "interests": person.get('interests', []),
            "preferences": person.get('preferences', {}),
            "deceased": person.get('deceased', False)
        }
        if 'birthday' in person:
            try:
                bd_parts = person['birthday'].split('.')
                if len(bd_parts) == 3:
                    birth_year = int(bd_parts[2])
                    info['age'] = datetime.now().year - birth_year
            except:
                pass
        return json.dumps(info, ensure_ascii=False)

    async def get_upcoming_events(self, **kwargs) -> str:
        """
        Возвращает список ближайших событий.
        Принимает параметр days (или его синонимы days_ahead, days_forward и т.п.)
        """
        # Извлекаем значение days из возможных вариантов
        days = None
        for key in ['days', 'days_ahead', 'days_forward', 'days_in_advance']:
            if key in kwargs:
                try:
                    days = int(kwargs[key])
                    break
                except (ValueError, TypeError):
                    continue

        if days is None:
            days = 30  # значение по умолчанию

        upcoming = self._get_upcoming_events_data(days)
        result = {
            "events": upcoming,
            "message": "Нет ближайших событий." if not upcoming else None
        }
        return json.dumps(result, ensure_ascii=False)

    def _get_upcoming_events_data(self, days: int = 30) -> List[Dict]:
        today = datetime.now()
        upcoming = []
        events = self.family_data.get('events', [])

        for event in events:
            date_str = event.get('date')
            if not date_str:
                continue
            try:
                # Парсим дату (поддерживаем ДД.ММ и ГГГГ)
                parts = date_str.split('.')
                if len(parts) == 2:  # ДД.ММ
                    day, month = int(parts[0]), int(parts[1])
                    event_date = datetime(today.year, month, day)
                    if event_date < today:
                        event_date = datetime(today.year + 1, month, day)
                    days_until = (event_date - today).days
                    if days_until <= days:
                        upcoming.append({
                            "name": event.get('event'),
                            "date": event_date.strftime("%d.%m"),
                            "days": days_until,
                            "type": event.get('type'),
                            "people_involved": event.get('people_involved', [])
                        })
                elif len(parts) == 1:  # только год
                    year = int(parts[0])
                    if year == today.year:
                        upcoming.append({
                            "name": event.get('event'),
                            "date": str(year),
                            "days": 0,
                            "type": event.get('type')
                        })
            except:
                continue

        upcoming.sort(key=lambda x: x['days'])
        return upcoming

    async def add_event(self, event_text: str) -> str:
        """Добавляет семейное событие."""
        event = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'text': event_text,
            'added_by': 'user'
        }
        self._save_event(event)
        return f"✅ Событие добавлено: {event_text}"

    async def add_reminder(self, text: str) -> str:
        """Создаёт напоминание (сохраняет в reminders.txt)."""
        reminders_file = self.agent_data_path / "reminders.txt"
        with open(reminders_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {text}\n")
        return f"✅ Напоминание добавлено: {text}"