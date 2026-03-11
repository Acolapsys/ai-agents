#!/bin/bash
cd ~/ai-agents

# Убиваем старую сессию, если есть
tmux kill-session -t agents 2>/dev/null

# Создаём новую сессию
tmux new-session -d -s agents -n main

# Запускаем каждый сервис в отдельном окне
tmux new-window -t agents -n secretary "cd services/secretary && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n family "cd services/family && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n architect "cd services/architect && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n english "cd services/english_mentor && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n mentor "cd services/mentor && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n designer "cd services/designer && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n gateway "cd services/gateway && source venv/bin/activate && ./run.sh"
tmux new-window -t agents -n process-manager "cd services/process-manager && source venv/bin/activate && ./run.sh"
# tmux new-window -t agents -n game "cd ~/projects/word-storm/backend && source venv/bin/activate && ./run.sh"

# Подключаемся к сессии
tmux attach -t agents