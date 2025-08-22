from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import os
from datetime import datetime

from app.database import get_db
from app.models import Note
from app.schemas import NoteCreate, NoteResponse
from apps.api.user_service.app.auth import get_current_user
from apps.api.shared.embeddings import get_embedding_service
from apps.api.shared.search import get_vector_search_service, get_text_search_service

router = APIRouter()

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

async def generate_title_from_ai(body: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AI_SERVICE_URL}/generate_title", json={"body": body})
        response.raise_for_status()
        return response.json()["title"]

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not note.title and note.body:
        # Generate title using AI service
        generated_title = await generate_title_from_ai(note.body)
        note.title = generated_title
    elif not note.title and not note.body:
        note.title = "Untitled Note"

    # Generate embeddings
    embedding_service = get_embedding_service()
    embeddings = await embedding_service.generate_note_embeddings(note.title, note.body)
    
    # Create note with embeddings
    db_note = Note(
        title=note.title,
        body=note.body,
        user_id=current_user["user_id"],
        title_embedding=embeddings["title_embedding"],
        body_embedding=embeddings["body_embedding"],
        combined_embedding=embeddings["combined_embedding"],
        embedding_model=embedding_service.model_name,
        embedding_created_at=datetime.utcnow(),
        content_hash=embedding_service.generate_content_hash(note.title, note.body),
        tags=note.tags if hasattr(note, 'tags') else None
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/", response_model=List[NoteResponse])
def read_notes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Note).filter(Note.user_id == current_user["user_id"]).all()

@router.get("/{note_id}", response_model=NoteResponse)
def read_note(note_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user["user_id"]).first()
    if db_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note: NoteCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user["user_id"]).first()
    if db_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if not note.title and note.body:
        # Generate title using AI service
        generated_title = await generate_title_from_ai(note.body)
        note.title = generated_title
    elif not note.title and not note.body:
        note.title = "Untitled Note"

    # Check if content has changed by comparing hash
    embedding_service = get_embedding_service()
    new_content_hash = embedding_service.generate_content_hash(note.title, note.body)
    
    if db_note.content_hash != new_content_hash:
        # Content has changed, regenerate embeddings
        embeddings = await embedding_service.generate_note_embeddings(note.title, note.body)
        
        db_note.title_embedding = embeddings["title_embedding"]
        db_note.body_embedding = embeddings["body_embedding"]
        db_note.combined_embedding = embeddings["combined_embedding"]
        db_note.embedding_model = embedding_service.model_name
        db_note.embedding_created_at = datetime.utcnow()
        db_note.content_hash = new_content_hash

    db_note.title = note.title
    db_note.body = note.body
    db_note.tags = note.tags if hasattr(note, 'tags') else db_note.tags
    db.commit()
    db.refresh(db_note)
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user["user_id"]).first()
    if db_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return

@router.get("/search/text")
async def search_notes_text(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search notes using traditional text search"""
    text_search = get_text_search_service()
    results = text_search.search_notes(db, current_user["user_id"], query, limit)
    return {"query": query, "results": results, "search_type": "text"}

@router.get("/search/semantic")
async def search_notes_semantic(
    query: str,
    limit: int = 10,
    similarity_threshold: float = 0.7,
    search_type: str = "combined",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search notes using vector similarity (semantic search)"""
    vector_search = get_vector_search_service()
    results = await vector_search.search_notes(
        db, current_user["user_id"], query, limit, similarity_threshold, search_type
    )
    
    # Format results for API response
    formatted_results = [
        {
            "note": note_data,
            "similarity_score": score
        }
        for note_data, score in results
    ]
    
    return {
        "query": query,
        "results": formatted_results,
        "search_type": "semantic",
        "similarity_threshold": similarity_threshold,
        "embedding_field": search_type
    }
