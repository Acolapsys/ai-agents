#!/bin/bash

echo "🔍 Проверка Ollama..."

# Проверка процесса
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Процесс Ollama запущен (PID: $(pgrep -x ollama))"
else
    echo "❌ Процесс Ollama не запущен"
fi

# Проверка API
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ API Ollama отвечает"
    
    # Показываем модели
    echo "📦 Установленные модели:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool | grep -E '"name"|"size"' | head -10
else
    echo "❌ API Ollama не отвечает"
fi

# Проверка моделей через CLI
if command -v ollama &> /dev/null; then
    echo "📋 Список моделей (ollama list):"
    ollama list 2>/dev/null || echo "   Не удалось получить список"
else
    echo "❌ Команда ollama не найдена"
fi

echo ""
echo "💡 Советы:"
echo "  • Запустить Ollama: ollama serve &"
echo "  • Скачать модель: ollama pull qwen2.5:7b"
echo "  • Проверить версию: ollama --version"
