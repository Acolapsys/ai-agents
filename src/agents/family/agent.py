#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Добавляем путь к корневой папке проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from core.agent import BaseAgent

class FamilyAgent(BaseAgent):
    """
    Елена - семейный советник.
    Помогает с семейными вопросами, напоминает о важных датах,
    даёт советы по подаркам и отношениям.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        print("👪 FamilyAgent.__init__: start")
        super().__init__(config_path)
        
        self.display_name = "Елена"
        
        # Загружаем данные о семье
        self.family_data = self._load_family_data()
        print(f"📊 Загружены семейные данные: {self.family_data}")
        
        # Загружаем историю семейных событий
        self.events_history = self._load_events_history()
        
        self.logger.info(f"✅ Агент {self.display_name} инициализирован")
        print("👪 FamilyAgent.__init__: end")
    
    def _load_family_data(self) -> Dict[str, Any]:
        """Загружает данные о семье из YAML"""
        family_file = self.get_storage_path('family', 'members.yaml')
        print(f"🔍 Ищем файл: {family_file}")
        
        if family_file.exists():
            with open(family_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                print(f"✅ Данные загружены: {list(data.keys())}")
                return data
        
        print("❌ Файл не найден")
        return {}
    
    def _load_events_history(self) -> List[Dict]:
        """Загружает историю семейных событий"""
        events_file = self.get_storage_path('family', 'events.json')
        
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return []
    
    def _save_event(self, event: Dict):
        """Сохраняет событие в историю"""
        self.events_history.append(event)
        
        if len(self.events_history) > 100:
            self.events_history = self.events_history[-100:]
        
        events_file = self.get_storage_path('family', 'events.json')
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(self.events_history, f, ensure_ascii=False, indent=2)
    
    def _find_person(self, name_query: str) -> Optional[Dict]:
        """Ищет человека по имени или отношению"""
        name_query = name_query.lower().strip()
        
        # Словарь соответствий
        relations = {
            'жена': 'spouse', 'супруга': 'spouse', 'эля': 'spouse', 'элеонора': 'spouse',
            'лиля': 'children', 'лилия': 'children',
            'дамир': 'children',
            'амелия': 'children',
            'татьяна': 'parents', 'тёща': 'parents',
            'марат': 'brother', 'брат': 'brother'
        }
        
        # Проверяем по ключевым словам
        for key, category in relations.items():
            if key in name_query:
                if category == 'spouse':
                    return self.family_data.get('spouse', {})
                elif category == 'children':
                    for child in self.family_data.get('children', []):
                        if key in child.get('name', '').lower():
                            return child
                elif category == 'parents':
                    return self.family_data.get('parents', {}).get('mother_in_law', {})
                elif category == 'brother':
                    return self.family_data.get('parents', {}).get('brother', {})
        
        # Прямой поиск по имени
        # Супруга
        spouse = self.family_data.get('spouse', {})
        if name_query in spouse.get('name', '').lower() or name_query in spouse.get('full_name', '').lower():
            return spouse
        
        # Дети
        for child in self.family_data.get('children', []):
            if name_query in child.get('name', '').lower():
                return child
        
        # Родители/родственники
        for rel_name, rel_data in self.family_data.get('parents', {}).items():
            if name_query in rel_data.get('name', '').lower():
                return rel_data
        
        return None
    
    def _get_upcoming_birthdays(self, days: int = 14) -> List[Dict]:
        """Возвращает список ближайших дней рождения"""
        today = datetime.now()
        upcoming = []
        
        # Все люди, у которых есть день рождения
        people = []
        
        # Супруга
        spouse = self.family_data.get('spouse', {})
        if spouse and 'birthday' in spouse:
            people.append(('spouse', spouse))
        
        # Дети
        for child in self.family_data.get('children', []):
            if 'birthday' in child:
                people.append(('child', child))
        
        # Родители/родственники
        for rel_name, rel_data in self.family_data.get('parents', {}).items():
            if 'birthday' in rel_data:
                people.append(('relative', rel_data))
        
        for rel_type, person in people:
            try:
                bd_str = person['birthday']
                # Парсим дату (поддерживаем форматы ДД.ММ.ГГГГ и ДД.ММ)
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
            except Exception as e:
                print(f"Ошибка парсинга даты {person.get('birthday')}: {e}")
                continue
        
        upcoming.sort(key=lambda x: x['days'])
        return upcoming
    
    def _get_gift_advice(self, person_name: str) -> str:
        """Даёт совет по подарку для конкретного человека"""
        person = self._find_person(person_name)
        
        if not person:
            return f"Расскажи мне о {person_name} подробнее, и я помогу с выбором подарка."
        
        name = person.get('name', person_name)
        
        # Проверяем предпочтения
        if 'preferences' in person and 'gifts' in person['preferences']:
            gifts = person['preferences']['gifts']
            return f"Для {name} можно подарить: {', '.join(gifts)}."
        
        if 'interests' in person:
            interests = person['interests']
            return f"{name} интересуется: {', '.join(interests)}. Можно подарить что-то из этого."
        
        # Специфичные советы
        if 'spouse' in str(person):
            return f"Для {name} всегда хороши цветы, внимание и забота. Может, устроить романтический вечер?"
        elif 'child' in str(person) or any(child in str(person) for child in ['Лилия', 'Дамир', 'Амелия']):
            return f"{name} ещё молод(а), возможно, стоит подарить что-то для развития или хобби."
        
        return f"Я пока мало знаю о {name}. Расскажи, что она/он любит?"
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает входящие сообщения"""
        if not update.message or not update.message.text:
            return
        
        user = update.effective_user
        message = update.message.text.strip()
        
        self.logger.info(f"📨 Сообщение от {user.first_name}: {message[:50]}...")
        
        response = await self._process_request(message)
        
        self.logger.info(f"📤 Ответ: {response[:50]}...")
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def _process_request(self, message: str) -> str:
        """Обрабатывает запрос к семейному советнику"""
        msg_lower = message.lower()
        
        # Команды
        if msg_lower in ['/start', 'start', 'привет', 'здравствуй']:
            return self._get_welcome()
        
        if msg_lower in ['/help', 'помощь', 'что ты умеешь']:
            return self._get_help()
        
        # Показать семейные данные
        if msg_lower in ['семья', 'моя семья', 'состав семьи']:
            return self._show_family()
        
        # Ближайшие дни рождения
        if any(word in msg_lower for word in ['дни рождения', 'ближайшие', 'кому скоро', 'др']):
            return self._show_upcoming_birthdays()
        
        # Совет по подарку
        if msg_lower.startswith('что подарить') or 'подарок' in msg_lower:
            return await self._handle_gift_advice(message)
        
        # Напомнить о событии
        if msg_lower.startswith('напомни о') or 'важная дата' in msg_lower:
            return await self._handle_reminder(message)
        
        # Что сегодня?
        if msg_lower in ['что сегодня', 'сегодня', 'события сегодня']:
            return self._show_today_events()
        
        # Добавить событие
        if msg_lower.startswith('добавь событие') or msg_lower.startswith('запомни'):
            return await self._add_event(message)
        
        # Общий разговор
        return self._get_general_response(message)
    
    def _show_family(self) -> str:
        """Показывает информацию о семье"""
        if not self.family_data:
            return "📭 Семейные данные ещё не загружены. Нужно создать файл data/family/members.yaml"
        
        result = "👪 *Наша семья:*\n\n"
        
        # Супруга
        spouse = self.family_data.get('spouse', {})
        if spouse:
            result += f"👩 *{spouse.get('name', 'жена')}*"
            if 'birthday' in spouse:
                result += f" — др {spouse['birthday']}"
            if 'preferences' in spouse and 'hobbies' in spouse['preferences']:
                result += f"\n   Любит: {', '.join(spouse['preferences']['hobbies'])}"
            result += "\n\n"
        
        # Дети
        children = self.family_data.get('children', [])
        if children:
            result += "👶 *Дети:*\n"
            for child in children:
                result += f"• {child.get('name')}"
                if 'age' in child:
                    result += f", {child['age']} лет"
                if 'birthday' in child:
                    result += f" (др {child['birthday']})"
                if 'interests' in child:
                    result += f"\n  Интересы: {', '.join(child['interests'])}"
                result += "\n"
            result += "\n"
        
        # Родители
        parents = self.family_data.get('parents', {})
        if parents:
            result += "👴 *Родители:*\n"
            for parent_type, parent in parents.items():
                result += f"• {parent.get('name', parent_type)}"
                if 'birthday' in parent:
                    result += f" (др {parent['birthday']})"
                result += "\n"
        
        return result
    
    def _show_upcoming_birthdays(self) -> str:
        """Показывает ближайшие дни рождения"""
        upcoming = self._get_upcoming_birthdays(days=30)
        
        if not upcoming:
            return "📅 В ближайший месяц дней рождений нет."
        
        result = "🎂 *Ближайшие дни рождения:*\n\n"
        for person in upcoming:
            days_word = "день" if person['days'] == 1 else "дня" if 2 <= person['days'] <= 4 else "дней"
            result += f"• *{person['name']}* — через {person['days']} {days_word} ({person['date']})\n"
            
            # Добавляем совет по подарку для близких
            if person['days'] <= 7:
                result += f"  💝 Совет: {self._get_gift_advice(person['name'])}\n"
        
        return result
    
    async def _handle_gift_advice(self, message: str) -> str:
        """Даёт совет по подарку"""
        # Извлекаем имя
        gift_for = message.lower()
        for word in ['что подарить', 'подарок', 'для']:
            gift_for = gift_for.replace(word, '')
        gift_for = gift_for.strip()
        
        if not gift_for or gift_for == 'жене':
            gift_for = 'жена'  # По умолчанию
        
        return self._get_gift_advice(gift_for)
    
    async def _handle_reminder(self, message: str) -> str:
        """Создаёт напоминание о событии"""
        event_text = message
        for word in ['напомни о', 'важная дата']:
            event_text = event_text.replace(word, '')
        event_text = event_text.strip()
        
        if not event_text:
            return "О чём напомнить? Например: `напомни о дне рождения тёщи 26 февраля`"
        
        reminders_file = self.get_storage_path('family', 'reminders.txt')
        with open(reminders_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {event_text}\n")
        
        return f"✅ Запомнила: {event_text}. Я напомню!"
    
    def _show_today_events(self) -> str:
        """Показывает события на сегодня"""
        today = datetime.now().strftime("%d.%m")
        reminders = []
        
        important_dates = self.family_data.get('important_dates', [])
        for date_info in important_dates:
            if date_info.get('date') == today:
                event = date_info.get('event', 'событие')
                people = date_info.get('people_involved', [])
                reminders.append(f"🔔 Сегодня {event}! {', '.join(people)}")
        
        if not reminders:
            return "📅 На сегодня никаких особых событий нет."
        
        result = "📌 *Сегодня:*\n\n"
        for r in reminders:
            result += f"{r}\n"
        
        return result
    
    async def _add_event(self, message: str) -> str:
        """Добавляет семейное событие"""
        event_text = message
        for word in ['добавь событие', 'запомни']:
            event_text = event_text.replace(word, '')
        event_text = event_text.strip()
        
        if not event_text:
            return "Что запомнить? Например: `запомни: Миша пошёл в школу 1 сентября`"
        
        event = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'text': event_text,
            'added_by': 'user'
        }
        self._save_event(event)
        
        return f"✅ Запомнила: {event_text}"
    
    def _get_general_response(self, message: str) -> str:
        """Общий ответ без нейросети"""
        message_lower = message.lower()
        
        if 'как дела' in message_lower:
            return "У меня всё хорошо, спасибо! Как дела в семье? Всё ли в порядке?"
        
        if 'спасибо' in message_lower:
            return "Пожалуйста! Я всегда рада помочь."
        
        if 'погода' in message_lower:
            return "Я пока не умею смотреть погоду, но могу напомнить взять зонтик, если нужно ☔️"
        
        if 'люблю' in message_lower:
            return "Это так трогательно ❤️ Семья - это самое важное."
        
        return ("Я тебя внимательно слушаю. Расскажи, что происходит в семье, "
                "или спроси про дни рождения, подарки. Я всегда рядом!")
    
    def _get_welcome(self) -> str:
        """Приветственное сообщение"""
        upcoming = self._get_upcoming_birthdays(days=7)
        upcoming_text = ""
        if upcoming:
            upcoming_text = f"\n\n🎂 Кстати, скоро день рождения у {upcoming[0]['name']} (через {upcoming[0]['days']} дней)."
        
        return (f"Здравствуй, {self.user_name}! Я Елена, твой семейный советник.\n\n"
                f"Я знаю всё о вашей семье и всегда готова помочь:\n"
                f"• напомнить о днях рождения\n"
                f"• подсказать, что подарить\n"
                f"• сохранить важные даты\n"
                f"• просто поддержать разговор{upcoming_text}\n\n"
                f"Напиши 'помощь' для списка команд.")
    
    def _get_help(self) -> str:
        """Справка по командам"""
        return (f"*Команды {self.display_name}:*\n\n"
                f"👪 *Семья:*\n"
                f"• семья — состав семьи\n"
                f"• дни рождения — ближайшие др\n"
                f"• что сегодня — события на сегодня\n\n"
                f"🎁 *Подарки:*\n"
                f"• что подарить [кому] — совет\n"
                f"• подарок для [имя] — совет\n\n"
                f"📅 *События:*\n"
                f"• добавить событие [текст]\n"
                f"• напомни о [событии]\n"
                f"• запомни [текст]\n\n"
                f"❓ *Другое:*\n"
                f"• помощь — эта справка")


def main():
    """Запускает бота"""
    print("🚀 Запуск Елены (семейного советника)...")
    
    token = os.environ.get('FAMILY_TOKEN')
    if not token:
        token_file = Path.home() / 'ai-agents' / 'config' / 'tokens.env'
        if token_file.exists():
            with open(token_file, 'r') as f:
                for line in f:
                    if line.startswith('FAMILY_TOKEN='):
                        token = line.strip().split('=', 1)[1].strip()
                        break
    
    if not token:
        print("❌ Токен не найден! Нужно добавить FAMILY_TOKEN=... в config/tokens.env")
        return
    
    agent = FamilyAgent()
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_message))
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")

if __name__ == '__main__':
    main()
