from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timedelta


from sqlalchemy import func, extract
from collections import Counter
import calendar


from .database import SessionLocal, UserAction

app = FastAPI(title="User Activity Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # адрес Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ActionCreate(BaseModel):
    action_type: str
    details: dict
    source: Optional[str] = None
    user_id: str = "user"

@app.post("/track")
async def track_action(action: ActionCreate, db: Session = Depends(get_db)):
    db_action = UserAction(
        timestamp=datetime.utcnow(),
        user_id=action.user_id,
        action_type=action.action_type,
        details=action.details,
        source=action.source
    )
    db.add(db_action)
    db.commit()
    return {"status": "ok"}

@app.get("/actions")
async def get_actions(
    limit: int = 100,
    action_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(UserAction)
    if action_type:
        query = query.filter(UserAction.action_type == action_type)
    return query.order_by(UserAction.timestamp.desc()).limit(limit).all()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "tracker"}

@app.get("/stats/tasks/daily")
async def tasks_daily(days: int = 30, db: Session = Depends(get_db)):
    """Количество созданных задач по дням за последние N дней."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    actions = db.query(UserAction).filter(
        UserAction.action_type == "task_created",
        UserAction.timestamp >= cutoff
    ).all()
    # группируем по дате
    daily_counts = {}
    for action in actions:
        date_str = action.timestamp.strftime("%Y-%m-%d")
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
    # сортируем по дате
    result = [{"date": d, "count": daily_counts[d]} for d in sorted(daily_counts.keys())]
    return result

@app.get("/stats/chat/agents")
async def chat_by_agent(db: Session = Depends(get_db)):
    """Количество сообщений (user и assistant) по каждому агенту."""
    actions = db.query(UserAction).filter(UserAction.action_type == "chat").all()
    agent_counts = Counter()
    for action in actions:
        source = action.source or "unknown"
        agent_counts[source] += 1
    return [{"agent": k, "count": v} for k, v in agent_counts.items()]

@app.get("/stats/activity/hourly")
async def hourly_activity(db: Session = Depends(get_db)):
    """Активность по часам (0-23)."""
    actions = db.query(UserAction).all()
    hourly = [0]*24
    for action in actions:
        hour = action.timestamp.hour
        hourly[hour] += 1
    return [{"hour": i, "count": hourly[i]} for i in range(24)]

@app.get("/stats/tasks/status")
async def tasks_by_status(db: Session = Depends(get_db)):
    """Текущее распределение задач по статусам (можно брать из task-manager, но проще из трекера)."""
    # Но трекер хранит только события, а не текущее состояние. Поэтому для этой статистики лучше напрямую из task-manager.
    # Пока пропустим.
    pass

# Также можно добавить эндпоинт для активности по дням недели
@app.get("/stats/activity/weekday")
async def activity_by_weekday(db: Session = Depends(get_db)):
    actions = db.query(UserAction).all()
    weekdays = [0]*7
    for action in actions:
        wd = action.timestamp.weekday()
        weekdays[wd] += 1
    return [{"weekday": calendar.day_name[i], "count": weekdays[i]} for i in range(7)]