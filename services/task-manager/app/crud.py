from sqlalchemy.orm import Session
from . import models, schemas

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: models.TaskStatus = None,
    priority: models.TaskPriority = None,
    assignee: str = None,
    search: str = None,
    project: str = None
):
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if assignee:
        query = query.filter(models.Task.assignee == assignee)
    if project:
        query = query.filter(models.Task.project == project)

    # Выполняем запрос без поиска по словам, получаем все задачи
    all_tasks = query.all()

    # Если есть поиск, фильтруем в Python
    if search:
        words = [word.strip().lower().replace('ё', 'е') for word in search.split() if word.strip()]
        filtered = []
        for task in all_tasks:
            title = (task.title or '').lower().replace('ё', 'е')
            description = (task.description or '').lower().replace('ё', 'е')
            if all(word in title or word in description for word in words):
                filtered.append(task)
    else:
        filtered = all_tasks

    # Применяем пагинацию
    paginated = filtered[skip:skip+limit]
    return paginated

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task