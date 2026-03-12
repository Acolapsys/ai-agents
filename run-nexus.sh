#!/bin/bash

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧠 Запуск Nexus - центра управления агентами${NC}"

cd ~/ai-agents

# Функция проверки, запущен ли процесс на порту
check_port() {
  if ss -tuln | grep ":$1 " > /dev/null; then
    return 0
  else
    return 1
  fi
}

# Функция запуска сервиса в фоне
start_service() {
  local name=$1
  local port=$2
  local script=$3

  if check_port $port; then
    echo -e "${GREEN}✅ $name уже запущен на порту $port${NC}"
  else
    echo -e "${YELLOW}🔄 Запуск $name на порту $port...${NC}"
    cd $script
    source venv/bin/activate
    nohup ./run.sh > /dev/null 2>&1 &
    cd ~/ai-agents
    sleep 2
    if check_port $port; then
      echo -e "${GREEN}✅ $name запущен${NC}"
    else
      echo -e "${RED}❌ Не удалось запустить $name${NC}"
    fi
  fi
}

# Запускаем process-manager (порт 8008)
start_service "Process Manager" 8008 "services/process-manager"

# Запускаем gateway (порт 8000)
start_service "Gateway" 8000 "services/gateway"

# Запускаем gateway (порт 8009)
start_service "Task Manager" 8009 "services/task-manager"

# Запускаем агентов (можно добавить по необходимости)
# Например, дизайнер (порт 8007)
# start_service "Designer Agent" 8007 "services/designer"

# Запускаем фронтенд
if pgrep -f "npm run dev" > /dev/null; then
  echo -e "${YELLOW}⚠️  Фронтенд уже запущен, пропускаем${NC}"
else
  echo -e "${YELLOW}🔄 Запуск фронтенда...${NC}"
  cd frontend
  npm run dev &
  cd ~/ai-agents
fi

# Ждём немного и показываем адрес
sleep 3
WSL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$WSL_IP" ]; then
  WSL_IP="localhost"
fi

echo -e "${GREEN}✅ Nexus запущен!${NC}"
echo -e "${GREEN}🌐 Откройте браузер по адресу: http://$WSL_IP:5173${NC}"
echo -e "${YELLOW}Если не открывается, попробуйте http://localhost:5173${NC}"