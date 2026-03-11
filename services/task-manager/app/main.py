from fastapi import FastAPI

app = FastAPI(title="Task Manager API")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "task-manager"}

@app.get("/")
async def root():
    return {"message": "Task Manager is running"}
