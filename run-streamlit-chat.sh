#!/bin/bash

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🎨 Запуск Streamlit-чата для дизайн-агента${NC}"

cd ~/ai-agents

# Проверяем, запущен ли дизайнер (порт 8007)
if ss -tuln | grep :8007 > /dev/null; then
    echo -e "${GREEN}✅ Агент дизайнер уже запущен на порту 8007${NC}"
else
    echo -e "${YELLOW}🔄 Запуск дизайн-агента...${NC}"
    cd services/designer
    source venv/bin/activate
    nohup ./run.sh > designer.log 2>&1 &
    echo -e "${GREEN}✅ Дизайнер запущен${NC}"
    cd ~/ai-agents
    sleep 3 # даём время агенту инициализироваться
fi

# Запускаем Streamlit-чат
echo -e "${YELLOW}🔄 Запуск Streamlit-чата...${NC}"
cd web_chat
streamlit run app.py &

# Ждём немного и показываем адрес
sleep 3
WSL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$WSL_IP" ]; then
    WSL_IP="localhost"
fi

echo -e "${GREEN}✅ Streamlit-чат запущен${NC}"
echo -e "${GREEN}🌐 Откройте браузер по адресу: http://$WSL_IP:8501${NC}"
echo -e "${YELLOW}Если не открывается, попробуйте http://localhost:8501 (если используете браузер в WSL)${NC}"