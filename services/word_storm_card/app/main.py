from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .agent import WordStormCardAgent

app = FastAPI(title="WordStorm Card Agent API")

# Создаём экземпляр агента (один на всё приложение)
agent = WordStormCardAgent()

class CardRequest(BaseModel):
    category: Optional[str] = None
    language: str = "ru"

class CardResponse(BaseModel):
    id: str
    target: str
    forbidden: list[str]
    category: str
    language: str
    created_at: str
    is_new: bool

class ManualCardUpload(BaseModel):
    cards: list[CardResponse]

@app.post("/generate", response_model=CardResponse)
async def generate_card(request: CardRequest):
    """Генерирует карточку по запросу"""
    card = await agent.get_card(request.category, request.language)
    return card

@app.post("/upload")
async def upload_manual_cards(upload: ManualCardUpload):
    """Загружает готовые карточки"""
    added = await agent.add_manual_cards([c.dict() for c in upload.cards])
    return {"status": "ok", "added": added}

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "WordStormCard"}
