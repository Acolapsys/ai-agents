#!/bin/bash

echo "🚀 Запуск Виктора Ивановича Лингвиста..."

# Переходим в папку проекта
cd ~/ai-agents

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем бота
cd src/agents/english_mentor
python agent.py
