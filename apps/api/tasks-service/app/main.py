from fastapi import FastAPI
from app.database import init_tasks_db
from app.routes import router as tasks_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_tasks_db()

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

@app.get("/")
async def read_root():
    return {"message": "Tasks Service is running"}
