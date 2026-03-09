import streamlit as st
import requests
import json

# Конфигурация страницы
st.set_page_config(page_title="AI Agents Chat", page_icon="🤖", layout="wide")

# Заголовок
st.title("🤖 Чат с AI-агентами")
st.markdown("Выберите агента и отправьте сообщение")

# Боковая панель с выбором агента
with st.sidebar:
    st.header("Настройки")
    agent = st.selectbox(
        "Выберите агента",
        options=["designer", "mentor", "secretary", "family", "architect", "english_mentor"],
        index=0
    )
    port = st.number_input("Порт агента", min_value=8000, max_value=9000, value=8007, step=1)
    st.markdown("---")
    st.markdown("### Информация")
    st.markdown("Агенты работают на локальных портах. Убедитесь, что сервис запущен.")

# Основная область
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображаем историю сообщений
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Поле ввода
if prompt := st.chat_input("Введите сообщение..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Отправляем запрос к агенту
    with st.chat_message("assistant"):
        with st.spinner(f"Ожидание ответа от агента {agent}..."):
            try:
                response = requests.post(
                    f"http://localhost:{port}/chat",
                    json={"message": prompt, "user_id": "streamlit", "chat_id": "web"},
                    timeout=60  # увеличиваем таймаут
                )
                response.raise_for_status()
                answer = response.json().get("response", "Нет ответа")
            except requests.exceptions.Timeout:
                answer = "⏰ Превышено время ожидания ответа от агента."
            except Exception as e:
                answer = f"Ошибка соединения: {e}"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Если ответ содержит код, предлагаем его скопировать
    if "```" in answer:
        with st.expander("Показать код"):
            st.code(answer.split("```")[1], language="html")