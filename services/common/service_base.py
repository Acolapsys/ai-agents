import os
import asyncio
import threading
import logging
from pathlib import Path
from typing import Type, Optional
from fastapi import FastAPI
from telegram.ext import Application, MessageHandler, filters
from dotenv import load_dotenv

# Настраиваем базовое логирование (можно будет дополнить)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_telegram_bot(agent, token: str):
    """
    Запускает Telegram-бота в отдельном потоке с собственным event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_telegram_message))

    async def start_bot():
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(1)

    loop.create_task(start_bot())
    loop.run_forever()

def create_agent_app(
    agent_class: Type,
    service_name: str,
    default_port: int = 8000,
    telegram_token_env: str = "TELEGRAM_TOKEN",
    env_file: Optional[Path] = None
) -> FastAPI:
    """
    Создаёт и настраивает FastAPI-приложение для агента.

    :param agent_class: класс агента (должен быть наследником BaseAgent)
    :param service_name: имя сервиса (для логов и тегов)
    :param default_port: порт по умолчанию (используется для информации)
    :param telegram_token_env: имя переменной окружения с токеном Telegram
    :param env_file: путь к .env файлу (если None, ищет в папке сервиса)
    :return: FastAPI app
    """
    # Определяем путь к .env (если не передан, ищем в папке на уровень выше от common)
    if env_file is None:
        # Предполагаем, что этот файл лежит в services/common, а .env — в services/<service>/
        # Поднимаемся на два уровня вверх и спускаемся в папку сервиса
        current_dir = Path(__file__).parent.parent / service_name
        env_file = current_dir / ".env"
    else:
        env_file = Path(env_file)

    # Загружаем переменные окружения
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        logger.info(f"Loaded env from {env_file}")
    else:
        logger.warning(f"Env file not found: {env_file}")

    # Получаем токен Telegram
    token = os.environ.get(telegram_token_env)

    # Создаём экземпляр агента
    agent = agent_class()
    agent.telegram_token = token

    # Запускаем Telegram-бота в фоне, если токен есть
    if token:
        threading.Thread(target=run_telegram_bot, args=(agent, token), daemon=True).start()
        logger.info(f"Telegram bot for {service_name} started in background thread")
    else:
        logger.warning(f"Telegram bot not started for {service_name}")

    # Создаём FastAPI приложение
    app = FastAPI(title=f"{service_name.capitalize()} Agent API")

    # Эндпоинт для проверки здоровья
    @app.get("/health")
    async def health():
        return {"status": "ok", "agent": service_name}

    # Основной эндпоинт для чата
    from pydantic import BaseModel

    class ChatRequest(BaseModel):
        message: str
        user_id: str
        chat_id: str

    class ChatResponse(BaseModel):
        response: str

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        try:
            response = await agent.process_message(
                message=request.message,
                user_id=request.user_id,
                chat_id=request.chat_id
            )
            return ChatResponse(response=response)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Можно вернуть 500, но для Telegram-бота лучше отдать текст ошибки
            return ChatResponse(response=f"Произошла внутренняя ошибка: {str(e)}")

    return app