# ~/ai-agents/services/secretary/app/main.py
import os
import asyncio
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telegram.ext import Application, MessageHandler, filters
from pathlib import Path
from .agent import SecretaryAgent

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


app = FastAPI(title="Secretary Agent API")

# Инициализируем агента
agent = SecretaryAgent()
token = os.environ.get('SECRETARY_TOKEN')

if not token:
    token_file = Path.home() / 'ai-agents' / 'config' / 'tokens.env'
    if token_file.exists():
        with open(token_file, 'r') as f:
            for line in f:
                if line.startswith('SECRETARY_TOKEN='):
                    token = line.strip().split('=', 1)[1].strip()
                    break

if not token:
    print("❌ Токен не найден!")


agent.telegram_token = token

# ---- Telegram bot (запускается в фоне) ----
def run_telegram_bot():
    """Запускает Telegram бота в отдельном потоке со своим event loop"""
    # Создаём новый event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(agent.telegram_token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.handle_telegram_message))

    async def start_bot():
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # Бесконечно держим бота
        while True:
            await asyncio.sleep(1)

    loop.create_task(start_bot())
    loop.run_forever()


# Запускаем бота в фоновом потоке, если токен указан
if agent.telegram_token:
    threading.Thread(target=run_telegram_bot, daemon=True).start()
else:
    print("Telegram token not set, bot not started")


# ---- HTTP API ----
class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_id: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Принимает текстовое сообщение, обрабатывает агентом и возвращает ответ.
    """
    try:
        # Предположим, что у агента есть метод process_message, не зависящий от Update
        # Если такого нет, адаптируем handle_message
        response = await agent.process_message(request.message, request.user_id, request.chat_id)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "Secretary Agent"}