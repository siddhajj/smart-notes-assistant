from fastapi import FastAPI
from app.database import init_notes_db
from app.routes import router as notes_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_notes_db()

app.include_router(notes_router, prefix="/notes", tags=["notes"])

@app.get("/")
async def read_root():
    return {"message": "Notes Service is running"}
