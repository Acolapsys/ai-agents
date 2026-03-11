#!/bin/bash

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Остановка Nexus...${NC}"

# Функция остановки процесса по порту (для сервисов с фиксированными портами)
stop_by_port() {
  local port=$1
  local name=$2
  local pid=$(lsof -ti:$port 2>/dev/null)

  if [ -n "$pid" ]; then
    echo -e "${YELLOW}🔄 Останавливаю $name (PID: $pid) на порту $port...${NC}"
    kill -TERM $pid 2>/dev/null
    sleep 1
    if kill -0 $pid 2>/dev/null; then
      echo -e "${YELLOW}⚠️  $name не отвечает, принудительное завершение...${NC}"
      kill -KILL $pid 2>/dev/null
    fi
    echo -e "${GREEN}✅ $name остановлен${NC}"
  else
    echo -e "${YELLOW}⚠️  Процесс на порту $port не найден${NC}"
  fi
}

# Функция остановки всех uvicorn-процессов из нашей папки services
stop_all_agents() {
  echo -e "${YELLOW}🔄 Останавливаю всех агентов (uvicorn)...${NC}"
  # Ищем все uvicorn процессы, запущенные из ~/ai-agents/services
  pids=$(ps aux | grep uvicorn | grep "$HOME/ai-agents/services" | grep -v grep | awk '{print $2}')
  if [ -n "$pids" ]; then
    for pid in $pids; do
      echo -e "${YELLOW}   Останавливаю процесс $pid${NC}"
      kill -TERM $pid 2>/dev/null
    done
    sleep 2
    # Проверяем, остались ли
    remaining=$(ps aux | grep uvicorn | grep "$HOME/ai-agents/services" | grep -v grep | awk '{print $2}')
    if [ -n "$remaining" ]; then
      echo -e "${YELLOW}⚠️  Некоторые процессы не завершились, принудительно убиваем${NC}"
      for pid in $remaining; do
        kill -KILL $pid 2>/dev/null
      done
    fi
    echo -e "${GREEN}✅ Все агенты остановлены${NC}"
  else
    echo -e "${YELLOW}⚠️  Агенты не найдены${NC}"
  fi
}

# Функция остановки всех процессов фронтенда (npm run dev)
stop_frontend() {
  local pids=$(pgrep -f "npm run dev" | grep -v grep)
  if [ -n "$pids" ]; then
    echo -e "${YELLOW}🔄 Останавливаю фронтенд (PID: $pids)...${NC}"
    # Отправляем SIGTERM всем процессам
    for pid in $pids; do
      kill -TERM $pid 2>/dev/null
    done
    sleep 2
    # Проверяем, остались ли живые
    local remaining=$(pgrep -f "npm run dev" | grep -v grep)
    if [ -n "$remaining" ]; then
      echo -e "${YELLOW}⚠️  Некоторые процессы фронта не завершились, принудительное завершение...${NC}"
      for pid in $remaining; do
        kill -KILL $pid 2>/dev/null
      done
    fi
    echo -e "${GREEN}✅ Фронтенд остановлен${NC}"
  else
    echo -e "${YELLOW}⚠️  Фронтенд не найден${NC}"
  fi
}

# Останавливаем всех агентов
stop_all_agents

# Останавливаем process-manager и gateway по портам
# stop_by_port 8008 "Process Manager"
# stop_by_port 8000 "Gateway"

# Останавливаем фронтенд
# Останавливаем все процессы на портах фронтенда (5173-5176)
for port in 5173 5174 5175 5176; do
  stop_by_port $port "Frontend (port $port)"
done


echo -e "${GREEN}✅ Все процессы Nexus остановлены${NC}"