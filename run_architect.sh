#!/bin/bash

echo "🚀 Запуск Виктора - Главного архитектора"

# Переходим в папку проекта
cd ~/ai-agents

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем бота
echo "✅ Запускаем бота..."
cd src/agents/architect
python agent.py
