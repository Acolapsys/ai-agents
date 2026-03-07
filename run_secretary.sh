#!/bin/bash

echo "🚀 Запуск Михаила - личного секретаря"

# Переходим в папку проекта
cd ~/ai-agents

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем, запущен ли Ollama (пока не обязательно)
# if ! pgrep -x "ollama" > /dev/null; then
#     echo "Запускаем Ollama..."
#     ollama serve &
#     sleep 5
# fi

# Запускаем бота
echo "✅ Всё готово. Запускаем бота..."
cd src/agents/secretary
python agent.py
