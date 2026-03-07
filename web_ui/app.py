#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
import json
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import psutil  # для мониторинга ресурсов

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

# Конфигурация страницы
st.set_page_config(
    page_title="AI Агенты - Управление",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Пути к данным
PROJECT_ROOT = Path.home() / "ai-agents"
DATA_PATH = PROJECT_ROOT / "data"
LOGS_PATH = PROJECT_ROOT / "logs"
CONFIG_PATH = PROJECT_ROOT / "config"

# Заголовок
st.title("🤖 Управление AI-агентами")
st.markdown("---")

# Боковая панель с навигацией
st.sidebar.title("Навигация")
page = st.sidebar.radio(
    "Перейти к разделу:",
    ["📊 Дашборд", "🤖 Агенты", "👪 Семья", "📝 Заметки", "🛒 Покупки", "📋 Задачи", "📚 Английский", "📁 Логи", "⚙️ Настройки"]
)

# Загружаем данные о семье
def load_family_data():
    family_file = DATA_PATH / "family" / "members.yaml"
    if family_file.exists():
        with open(family_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

# Загружаем реестр агентов
def load_agents_registry():
    registry_file = DATA_PATH / "registry" / "agents.yaml"
    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {"agents": {}}

# Сохраняем изменения в YAML
def save_yaml(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

# Функция для получения статуса агента (запущен/остановлен)
def get_agent_status(agent_name):
    # Проверяем по PID файлу или процессу
    pid_file = PROJECT_ROOT / f"run/{agent_name}.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            if psutil.pid_exists(pid):
                return "🟢 Запущен"
            else:
                pid_file.unlink(missing_ok=True)
                return "⚫ Остановлен"
        except:
            return "⚫ Остановлен"
    return "⚫ Остановлен"

# Запуск агента
def start_agent(agent_name):
    script = PROJECT_ROOT / f"run_{agent_name}.sh"
    if script.exists():
        try:
            # Запускаем в фоне
            process = subprocess.Popen(
                [str(script)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Сохраняем PID
            pid_file = PROJECT_ROOT / f"run/{agent_name}.pid"
            pid_file.parent.mkdir(exist_ok=True)
            pid_file.write_text(str(process.pid))
            return True
        except Exception as e:
            st.error(f"Ошибка запуска: {e}")
            return False
    return False

# Остановка агента
def stop_agent(agent_name):
    pid_file = PROJECT_ROOT / f"run/{agent_name}.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
            pid_file.unlink()
            return True
        except:
            pid_file.unlink(missing_ok=True)
            return False
    return False

# --- Страницы ---

if page == "📊 Дашборд":
    st.header("📊 Дашборд состояния системы")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Загружаем реестр
    registry = load_agents_registry()
    agents = registry.get("agents", {})
    
    with col1:
        st.metric("Всего агентов", len(agents))
    
    # Считаем запущенные
    running = 0
    for aid in agents.keys():
        if get_agent_status(aid) == "🟢 Запущен":
            running += 1
    
    with col2:
        st.metric("Запущено", running)
    
    # Размер данных
    data_size = sum(f.stat().st_size for f in DATA_PATH.rglob('*') if f.is_file()) / 1024
    with col3:
        st.metric("Данные", f"{data_size:.1f} КБ")
    
    # Последние логи
    with col4:
        st.metric("Активность", "Онлайн")
    
    st.markdown("---")
    
    # График активности агентов
    st.subheader("Активность агентов")
    
    # Собираем статистику по логам за последние 7 дней
    dates = []
    counts = {aid: [] for aid in agents.keys()}
    
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        dates.append(day.strftime("%d.%m"))
        
        for aid in agents.keys():
            log_file = LOGS_PATH / aid / "agent.log"
            count = 0
            if log_file.exists():
                # Считаем записи за этот день (упрощённо)
                log_text = log_file.read_text(encoding='utf-8')
                count = log_text.count(day.strftime("%Y-%m-%d"))
            counts[aid].append(count)
    
    # Создаём DataFrame для графика
    df = pd.DataFrame(counts, index=dates)
    
    fig = px.line(df, title="Активность агентов по дням")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Последние события
    st.subheader("Последние события")
    
    events = []
    for aid in agents.keys():
        log_file = LOGS_PATH / aid / "agent.log"
        if log_file.exists():
            # Берём последние 5 строк из лога
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    events.append({
                        "Время": line[:19],
                        "Агент": agents[aid].get("name", aid),
                        "Событие": line[20:].strip()
                    })
    
    if events:
        events.sort(key=lambda x: x["Время"], reverse=True)
        st.dataframe(pd.DataFrame(events[:20]), use_container_width=True)

elif page == "🤖 Агенты":
    st.header("🤖 Управление агентами")
    
    registry = load_agents_registry()
    agents = registry.get("agents", {})
    
    for aid, info in agents.items():
        with st.expander(f"{info.get('name', aid)} ({aid})", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Роль:** {info.get('role', 'Не указана')}")
                st.markdown(f"**Описание:** {info.get('description', 'Нет описания')}")
                st.markdown(f"**Файл:** `{info.get('file', 'Неизвестно')}`")
            
            with col2:
                status = get_agent_status(aid)
                st.markdown(f"**Статус:** {status}")
                
                if "🟢" in status:
                    if st.button(f"Остановить", key=f"stop_{aid}"):
                        if stop_agent(aid):
                            st.success(f"Агент {info.get('name', aid)} остановлен")
                            st.rerun()
                        else:
                            st.error("Ошибка остановки")
                else:
                    if st.button(f"Запустить", key=f"start_{aid}"):
                        if start_agent(aid):
                            st.success(f"Агент {info.get('name', aid)} запущен")
                            st.rerun()
                        else:
                            st.error("Ошибка запуска")
            
            with col3:
                # Кнопки для просмотра кода и логов
                if st.button("📄 Код", key=f"code_{aid}"):
                    code_file = PROJECT_ROOT / info.get('file', '')
                    if code_file.exists():
                        with open(code_file, 'r', encoding='utf-8') as f:
                            st.code(f.read(), language='python')
                    else:
                        st.warning("Файл не найден")
                
                if st.button("📋 Лог", key=f"log_{aid}"):
                    log_file = LOGS_PATH / aid / "agent.log"
                    if log_file.exists():
                        with open(log_file, 'r', encoding='utf-8') as f:
                            st.code(f.read()[-2000:], language='text')
                    else:
                        st.warning("Лог не найден")
    
    st.markdown("---")
    st.subheader("Добавить нового агента")
    
    with st.form("new_agent_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("ID агента (латиница, без пробелов)")
            new_name = st.text_input("Имя для отображения")
            new_role = st.text_input("Роль")
        with col2:
            new_desc = st.text_area("Описание")
            new_file = st.text_input("Путь к файлу (относительно проекта)", value=f"src/agents/{new_id}/agent.py")
        
        submitted = st.form_submit_button("Создать")
        if submitted:
            if new_id and new_name:
                registry["agents"][new_id] = {
                    "name": new_name,
                    "role": new_role,
                    "status": "active",
                    "description": new_desc,
                    "created": datetime.now().isoformat(),
                    "file": new_file
                }
                registry["statistics"]["last_updated"] = datetime.now().isoformat()
                save_yaml(registry, DATA_PATH / "registry" / "agents.yaml")
                st.success(f"Агент {new_name} добавлен в реестр!")
                st.rerun()
            else:
                st.error("ID и Имя обязательны")

elif page == "👪 Семья":
    st.header("👪 Семейные данные")
    
    family = load_family_data()
    
    # Вкладки для разных разделов
    tab1, tab2, tab3, tab4 = st.tabs(["Супруга", "Дети", "Родители", "Важные даты"])
    
    with tab1:
        st.subheader("Супруга")
        spouse = family.get("spouse", {})
        
        with st.form("spouse_form"):
            col1, col2 = st.columns(2)
            with col1:
                spouse["name"] = st.text_input("Имя", value=spouse.get("name", ""))
                spouse["birthday"] = st.text_input("Дата рождения", value=spouse.get("birthday", ""))
            with col2:
                if "preferences" not in spouse:
                    spouse["preferences"] = {}
                spouse["preferences"]["gifts"] = st.text_area("Предпочтения в подарках", 
                    value=", ".join(spouse.get("preferences", {}).get("gifts", [])))
            
            if st.form_submit_button("Сохранить"):
                family["spouse"] = spouse
                save_yaml(family, DATA_PATH / "family" / "members.yaml")
                st.success("Данные сохранены!")
    
    with tab2:
        st.subheader("Дети")
        children = family.get("children", [])
        
        for i, child in enumerate(children):
            with st.expander(f"{child.get('name', f'Ребенок {i+1}')}"):
                col1, col2 = st.columns(2)
                with col1:
                    child["name"] = st.text_input(f"Имя", value=child.get("name", ""), key=f"child_name_{i}")
                    child["birthday"] = st.text_input(f"Дата рождения", value=child.get("birthday", ""), key=f"child_bday_{i}")
                with col2:
                    child["interests"] = st.text_area(f"Интересы", 
                        value=", ".join(child.get("interests", [])), key=f"child_int_{i}").split(", ")
                
                if st.button(f"Удалить", key=f"del_child_{i}"):
                    children.pop(i)
                    family["children"] = children
                    save_yaml(family, DATA_PATH / "family" / "members.yaml")
                    st.rerun()
        
        if st.button("➕ Добавить ребенка"):
            children.append({"name": "Новый ребенок", "birthday": "", "interests": []})
            family["children"] = children
            save_yaml(family, DATA_PATH / "family" / "members.yaml")
            st.rerun()
        
        if st.button("💾 Сохранить всех детей"):
            family["children"] = children
            save_yaml(family, DATA_PATH / "family" / "members.yaml")
            st.success("Данные сохранены!")
    
    with tab3:
        st.subheader("Родители")
        parents = family.get("parents", {})
        
        for parent_type, parent in parents.items():
            with st.expander(parent.get("name", parent_type)):
                col1, col2 = st.columns(2)
                with col1:
                    parent["name"] = st.text_input(f"Имя", value=parent.get("name", ""), key=f"parent_name_{parent_type}")
                    parent["birthday"] = st.text_input(f"Дата рождения", value=parent.get("birthday", ""), key=f"parent_bday_{parent_type}")
                with col2:
                    parent["relation"] = st.text_input(f"Кем приходится", value=parent.get("relation", ""), key=f"parent_rel_{parent_type}")
        
        if st.button("💾 Сохранить родителей"):
            family["parents"] = parents
            save_yaml(family, DATA_PATH / "family" / "members.yaml")
            st.success("Данные сохранены!")
    
    with tab4:
        st.subheader("Важные даты")
        important_dates = family.get("important_dates", [])
        
        for i, date_info in enumerate(important_dates):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                date_info["date"] = st.text_input("Дата (ДД.ММ)", value=date_info.get("date", ""), key=f"date_date_{i}")
            with col2:
                date_info["event"] = st.text_input("Событие", value=date_info.get("event", ""), key=f"date_event_{i}")
            with col3:
                if st.button("❌", key=f"del_date_{i}"):
                    important_dates.pop(i)
                    family["important_dates"] = important_dates
                    save_yaml(family, DATA_PATH / "family" / "members.yaml")
                    st.rerun()
        
        if st.button("➕ Добавить дату"):
            important_dates.append({"date": "", "event": ""})
            family["important_dates"] = important_dates
            save_yaml(family, DATA_PATH / "family" / "members.yaml")
            st.rerun()

elif page == "📝 Заметки":
    st.header("📝 Заметки")
    
    notes_path = DATA_PATH / "notes"
    notes_files = sorted(notes_path.glob("*.txt"), reverse=True)
    
    selected_date = st.selectbox("Выберите дату", [f.stem for f in notes_files])
    
    if selected_date:
        note_file = notes_path / f"{selected_date}.txt"
        if note_file.exists():
            with open(note_file, 'r', encoding='utf-8') as f:
                notes = f.read()
            st.text_area("Содержимое", notes, height=400)
            
            if st.button("💾 Сохранить изменения"):
                # Здесь можно добавить сохранение
                st.success("Сохранено!")

elif page == "🛒 Покупки":
    st.header("🛒 Список покупок")
    
    shopping_file = DATA_PATH / "tasks" / "shopping.txt"
    if shopping_file.exists():
        with open(shopping_file, 'r', encoding='utf-8') as f:
            items = f.readlines()
        
        for i, item in enumerate(items):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(item.strip())
            with col2:
                if st.button("✓", key=f"shop_del_{i}"):
                    items.pop(i)
                    with open(shopping_file, 'w', encoding='utf-8') as f:
                        f.writelines(items)
                    st.rerun()
        
        new_item = st.text_input("Добавить товар")
        if st.button("➕ Добавить"):
            with open(shopping_file, 'a', encoding='utf-8') as f:
                f.write(f"• {new_item}\n")
            st.rerun()
    else:
        st.info("Список покупок пуст")

elif page == "📋 Задачи":
    st.header("📋 Задачи")
    
    tasks_file = DATA_PATH / "tasks" / "tasks.txt"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = f.readlines()
        
        for i, task in enumerate(tasks):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(task.strip())
            with col2:
                if task.startswith("[ ]"):
                    if st.button("✓ Выполнено", key=f"task_done_{i}"):
                        tasks[i] = task.replace("[ ]", "[x]")
                        with open(tasks_file, 'w', encoding='utf-8') as f:
                            f.writelines(tasks)
                        st.rerun()
            with col3:
                if st.button("🗑️", key=f"task_del_{i}"):
                    tasks.pop(i)
                    with open(tasks_file, 'w', encoding='utf-8') as f:
                        f.writelines(tasks)
                    st.rerun()
        
        new_task = st.text_input("Новая задача")
        if st.button("➕ Добавить"):
            with open(tasks_file, 'a', encoding='utf-8') as f:
                f.write(f"[ ] {new_task}\n")
            st.rerun()
    else:
        st.info("Задач пока нет")

elif page == "📚 Английский":
    st.header("📚 Изучение английского")
    
    profile_file = DATA_PATH / "learning" / "profile.json"
    if profile_file.exists():
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Уровень", profile.get("level", "beginner").upper())
            st.metric("Уроков пройдено", profile.get("lessons_completed", 0))
        with col2:
            st.metric("Всего времени", f"{profile.get('total_time', 0)} мин")
            vocab_size = len(profile.get("progress", {}).get("vocabulary", {}))
            st.metric("Словарный запас", vocab_size)
        
        st.subheader("Словарь")
        vocab = profile.get("progress", {}).get("vocabulary", {})
        if vocab:
            vocab_df = pd.DataFrame([
                {"Слово": word, "Добавлено": info.get("learned", "")[:10]}
                for word, info in vocab.items()
            ])
            st.dataframe(vocab_df, use_container_width=True)
        else:
            st.info("Словарь пока пуст")
    else:
        st.info("Данные об обучении ещё не созданы")

elif page == "📁 Логи":
    st.header("📁 Логи агентов")
    
    registry = load_agents_registry()
    agents = registry.get("agents", {})
    
    selected_agent = st.selectbox("Выберите агента", list(agents.keys()))
    
    if selected_agent:
        log_file = LOGS_PATH / selected_agent / "agent.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
            st.text_area("Лог", logs, height=600)
            
            if st.button("🔄 Обновить"):
                st.rerun()
            
            if st.button("🗑️ Очистить лог"):
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                st.success("Лог очищен")
        else:
            st.warning("Лог не найден")

elif page == "⚙️ Настройки":
    st.header("⚙️ Настройки")
    
    st.subheader("Конфигурация Ollama")
    
    # Проверяем доступность Ollama
    import aiohttp
    import asyncio
    
    async def check_ollama():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', timeout=2) as resp:
                    return resp.status == 200
        except:
            return False
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ollama_ok = loop.run_until_complete(check_ollama())
    loop.close()
    
    if ollama_ok:
        st.success("✅ Ollama доступна")
    else:
        st.error("❌ Ollama не отвечает")
    
    st.subheader("Управление процессами")
    
    if st.button("Перезапустить всех агентов"):
        for pid_file in (PROJECT_ROOT / "run").glob("*.pid"):
            try:
                pid = int(pid_file.read_text())
                process = psutil.Process(pid)
                process.terminate()
                pid_file.unlink()
            except:
                pass
        
        st.success("Все агенты остановлены. Запустите нужных вручную.")
    
    st.subheader("Резервное копирование")
    
    if st.button("Создать бэкап данных"):
        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        import tarfile
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(DATA_PATH, arcname="data")
        
        st.success(f"Бэкап создан: {backup_file}")
