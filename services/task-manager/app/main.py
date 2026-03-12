from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas
from .database import SessionLocal, engine

# Создаём таблицы в БД (если ещё нет)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # адрес Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "task-manager"}

@app.get("/tasks", response_model=List[schemas.TaskInDB])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TaskStatus] = None,
    priority: Optional[models.TaskPriority] = None,
    assignee: Optional[str] = None,
    search: Optional[str] = None,
    project: Optional[str] = None,  # новый параметр
    db: Session = Depends(get_db)
):
    tasks = crud.get_tasks(
        db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        assignee=assignee,
        search=search,
        project=project
    )
    return tasks

@app.post("/tasks", response_model=schemas.TaskInDB)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.get("/tasks/{task_id}", response_model=schemas.TaskInDB)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskInDB)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", response_model=schemas.TaskInDB)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
