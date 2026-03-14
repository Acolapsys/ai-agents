from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

from .database import SessionLocal, UserAction

app = FastAPI(title="User Activity Tracker")

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