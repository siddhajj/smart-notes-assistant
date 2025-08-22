from fastapi import FastAPI
from app.database import init_search_db
from app.routes import router as search_router

app = FastAPI(title="Search Service", description="Unified search and RAG service for notes and tasks")

@app.on_event("startup")
def on_startup():
    init_search_db()

app.include_router(search_router, prefix="/search", tags=["search"])

@app.get("/")
async def read_root():
    return {"message": "Search Service is running", "features": ["text_search", "semantic_search", "rag"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "search"}