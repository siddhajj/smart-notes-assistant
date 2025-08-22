from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from apps.api.user_service.app.auth import get_current_user
from apps.api.shared.embeddings import get_embedding_service
from apps.api.shared.search import get_vector_search_service, get_text_search_service

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if task.due_date and not isinstance(task.due_date, date):
        try:
            task.due_date = date.fromisoformat(str(task.due_date))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid due date format. Use YYYY-MM-DD.")

    # Generate embeddings
    embedding_service = get_embedding_service()
    description_embedding = await embedding_service.generate_task_embedding(task.description)
    
    # Create task with embeddings
    db_task = Task(
        description=task.description,
        due_date=task.due_date,
        is_completed=task.is_completed if hasattr(task, 'is_completed') else False,
        user_id=current_user["user_id"],
        description_embedding=description_embedding,
        embedding_model=embedding_service.model_name,
        embedding_created_at=datetime.utcnow(),
        content_hash=embedding_service.generate_content_hash(task.description),
        tags=task.tags if hasattr(task, 'tags') else None,
        priority=task.priority if hasattr(task, 'priority') else "medium"
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
def read_tasks(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Task).filter(Task.user_id == current_user["user_id"]).all()

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["user_id"]).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["user_id"]).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.due_date and not isinstance(task.due_date, date):
        try:
            task.due_date = date.fromisoformat(str(task.due_date))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid due date format. Use YYYY-MM-DD.")

    # Check if description has changed by comparing hash
    embedding_service = get_embedding_service()
    new_content_hash = embedding_service.generate_content_hash(task.description)
    
    if db_task.content_hash != new_content_hash:
        # Content has changed, regenerate embeddings
        description_embedding = await embedding_service.generate_task_embedding(task.description)
        
        db_task.description_embedding = description_embedding
        db_task.embedding_model = embedding_service.model_name
        db_task.embedding_created_at = datetime.utcnow()
        db_task.content_hash = new_content_hash

    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.is_completed = task.is_completed if hasattr(task, 'is_completed') else db_task.is_completed
    db_task.tags = task.tags if hasattr(task, 'tags') else db_task.tags
    db_task.priority = task.priority if hasattr(task, 'priority') else db_task.priority
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user["user_id"]).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return

@router.get("/search/text")
async def search_tasks_text(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search tasks using traditional text search"""
    text_search = get_text_search_service()
    results = text_search.search_tasks(db, current_user["user_id"], query, limit)
    return {"query": query, "results": results, "search_type": "text"}

@router.get("/search/semantic")
async def search_tasks_semantic(
    query: str,
    limit: int = 10,
    similarity_threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search tasks using vector similarity (semantic search)"""
    vector_search = get_vector_search_service()
    results = await vector_search.search_tasks(
        db, current_user["user_id"], query, limit, similarity_threshold
    )
    
    # Format results for API response
    formatted_results = [
        {
            "task": task_data,
            "similarity_score": score
        }
        for task_data, score in results
    ]
    
    return {
        "query": query,
        "results": formatted_results,
        "search_type": "semantic",
        "similarity_threshold": similarity_threshold
    }