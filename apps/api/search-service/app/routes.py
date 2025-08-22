from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from apps.api.user_service.app.auth import get_current_user
from apps.api.shared.search import get_vector_search_service, get_text_search_service
from apps.api.shared.rag import get_rag_service

router = APIRouter()

class SearchResponse(BaseModel):
    query: str
    search_type: str
    results: dict
    total_results: int
    metadata: Optional[dict] = None

class RAGResponse(BaseModel):
    query: str
    search_results: dict
    ai_answer: Optional[dict]
    context_used: bool
    search_type: str
    total_results: int
    metadata: dict

@router.get("/", response_model=SearchResponse)
async def unified_search(
    query: str,
    search_type: str = Query("text", regex="^(text|semantic|combined)$"),
    limit: int = Query(10, ge=1, le=50),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0),
    embedding_field: str = Query("combined", regex="^(title|body|combined)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Unified search endpoint that supports both text and semantic search across notes and tasks
    
    - **query**: Search query text
    - **search_type**: "text", "semantic", or "combined" (both text and semantic)
    - **limit**: Maximum number of results per category
    - **similarity_threshold**: Minimum similarity score for semantic search (0.0-1.0)
    - **embedding_field**: For notes semantic search: "title", "body", or "combined"
    """
    
    vector_search = get_vector_search_service()
    text_search = get_text_search_service()
    
    user_id = current_user["user_id"]
    
    if search_type == "text":
        # Traditional text search
        results = text_search.search_combined(db, user_id, query, limit)
        formatted_results = {
            "notes": [
                {
                    "id": str(note.id),
                    "title": note.title,
                    "body": note.body,
                    "tags": note.tags or [],
                    "created_at": note.created_at,
                    "type": "note"
                }
                for note in results["notes"]
            ],
            "tasks": [
                {
                    "id": str(task.id),
                    "description": task.description,
                    "due_date": task.due_date,
                    "is_completed": task.is_completed,
                    "priority": task.priority or "medium",
                    "tags": task.tags or [],
                    "created_at": task.created_at,
                    "type": "task"
                }
                for task in results["tasks"]
            ]
        }
        
        metadata = {"search_method": "text_matching"}
        
    elif search_type == "semantic":
        # Vector similarity search
        results = await vector_search.search_combined(
            db, user_id, query, limit, similarity_threshold
        )
        
        formatted_results = {
            "notes": [
                {
                    "id": note_data["id"],
                    "title": note_data["title"],
                    "body": note_data["body"],
                    "tags": note_data.get("tags", []),
                    "created_at": note_data["created_at"],
                    "similarity_score": score,
                    "type": "note"
                }
                for note_data, score in results["notes"]
            ],
            "tasks": [
                {
                    "id": task_data["id"],
                    "description": task_data["description"],
                    "due_date": task_data.get("due_date"),
                    "is_completed": task_data.get("is_completed", False),
                    "priority": task_data.get("priority", "medium"),
                    "tags": task_data.get("tags", []),
                    "created_at": task_data["created_at"],
                    "similarity_score": score,
                    "type": "task"
                }
                for task_data, score in results["tasks"]
            ]
        }
        
        metadata = {
            "search_method": "vector_similarity",
            "similarity_threshold": similarity_threshold,
            "embedding_field": embedding_field
        }
        
    elif search_type == "combined":
        # Both text and semantic search
        text_results = text_search.search_combined(db, user_id, query, limit)
        semantic_results = await vector_search.search_combined(
            db, user_id, query, limit, similarity_threshold
        )
        
        formatted_results = {
            "text_search": {
                "notes": [
                    {
                        "id": str(note.id),
                        "title": note.title,
                        "body": note.body,
                        "tags": note.tags or [],
                        "created_at": note.created_at,
                        "type": "note",
                        "search_method": "text"
                    }
                    for note in text_results["notes"]
                ],
                "tasks": [
                    {
                        "id": str(task.id),
                        "description": task.description,
                        "due_date": task.due_date,
                        "is_completed": task.is_completed,
                        "priority": task.priority or "medium",
                        "tags": task.tags or [],
                        "created_at": task.created_at,
                        "type": "task",
                        "search_method": "text"
                    }
                    for task in text_results["tasks"]
                ]
            },
            "semantic_search": {
                "notes": [
                    {
                        "id": note_data["id"],
                        "title": note_data["title"],
                        "body": note_data["body"],
                        "tags": note_data.get("tags", []),
                        "created_at": note_data["created_at"],
                        "similarity_score": score,
                        "type": "note",
                        "search_method": "semantic"
                    }
                    for note_data, score in semantic_results["notes"]
                ],
                "tasks": [
                    {
                        "id": task_data["id"],
                        "description": task_data["description"],
                        "due_date": task_data.get("due_date"),
                        "is_completed": task_data.get("is_completed", False),
                        "priority": task_data.get("priority", "medium"),
                        "tags": task_data.get("tags", []),
                        "created_at": task_data["created_at"],
                        "similarity_score": score,
                        "type": "task",
                        "search_method": "semantic"
                    }
                    for task_data, score in semantic_results["tasks"]
                ]
            }
        }
        
        metadata = {
            "search_method": "combined",
            "text_results": len(text_results["notes"]) + len(text_results["tasks"]),
            "semantic_results": len(semantic_results["notes"]) + len(semantic_results["tasks"]),
            "similarity_threshold": similarity_threshold
        }
    
    total_results = _count_total_results(formatted_results)
    
    return SearchResponse(
        query=query,
        search_type=search_type,
        results=formatted_results,
        total_results=total_results,
        metadata=metadata
    )

@router.get("/ask", response_model=RAGResponse)
async def ask_question(
    question: str,
    search_type: str = Query("semantic", regex="^(text|semantic)$"),
    limit: int = Query(5, ge=1, le=20),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    RAG-powered question answering endpoint
    
    Ask questions about your notes and tasks and get AI-powered answers based on your content.
    
    - **question**: Your question about your notes/tasks
    - **search_type**: "text" or "semantic" search for finding relevant content
    - **limit**: Maximum number of items to use as context
    - **similarity_threshold**: Minimum similarity score for semantic search
    """
    
    rag_service = get_rag_service()
    
    result = await rag_service.ask_question(
        db=db,
        user_id=current_user["user_id"],
        question=question,
        search_type=search_type,
        limit=limit
    )
    
    return RAGResponse(**result)

@router.get("/rag")
async def rag_search(
    query: str,
    search_limit: int = Query(5, ge=1, le=20),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0),
    use_semantic_search: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Advanced RAG search that combines search with AI-generated insights
    
    - **query**: Search query or question
    - **search_limit**: Number of items to retrieve for context
    - **similarity_threshold**: Minimum similarity for semantic search
    - **use_semantic_search**: Whether to use semantic or text search
    """
    
    rag_service = get_rag_service()
    
    result = await rag_service.search_and_answer(
        db=db,
        user_id=current_user["user_id"],
        query=query,
        search_limit=search_limit,
        similarity_threshold=similarity_threshold,
        use_semantic_search=use_semantic_search
    )
    
    return result

def _count_total_results(results: dict) -> int:
    """Helper function to count total results in various result formats"""
    if "text_search" in results and "semantic_search" in results:
        # Combined search format
        text_count = len(results["text_search"]["notes"]) + len(results["text_search"]["tasks"])
        semantic_count = len(results["semantic_search"]["notes"]) + len(results["semantic_search"]["tasks"])
        return text_count + semantic_count
    elif "notes" in results and "tasks" in results:
        # Standard format
        return len(results["notes"]) + len(results["tasks"])
    else:
        return 0