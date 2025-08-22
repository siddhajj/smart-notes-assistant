from fastapi import FastAPI
from app.database import init_user_db
from app.routes import router as user_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_user_db()

app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
async def read_root():
    return {"message": "User Service is running"}
