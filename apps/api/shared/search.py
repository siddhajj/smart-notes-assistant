from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import logging

from apps.api.shared.embeddings import get_embedding_service

logger = logging.getLogger(__name__)

class VectorSearchService:
    """Service for performing vector similarity searches"""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
    
    async def search_notes(
        self, 
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        search_type: str = "combined"
    ) -> List[Tuple[Any, float]]:
        """
        Search notes using vector similarity
        
        Args:
            db: Database session
            user_id: User ID to filter by
            query: Search query text
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            search_type: "title", "body", or "combined" embedding to search
        
        Returns:
            List of (note, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_text_embedding(query)
        
        # Choose the embedding field to search
        embedding_field = {
            "title": "title_embedding",
            "body": "body_embedding", 
            "combined": "combined_embedding"
        }.get(search_type, "combined_embedding")
        
        # Perform vector similarity search using cosine similarity
        # Note: This uses pgvector's cosine similarity operator <=>
        search_query = text(f"""
            SELECT 
                notes.*,
                1 - (notes.{embedding_field} <=> :query_embedding) AS similarity_score
            FROM notes 
            WHERE 
                notes.user_id = :user_id 
                AND notes.{embedding_field} IS NOT NULL
                AND 1 - (notes.{embedding_field} <=> :query_embedding) >= :threshold
            ORDER BY similarity_score DESC
            LIMIT :limit
        """)
        
        try:
            result = db.execute(search_query, {
                "query_embedding": query_embedding,
                "user_id": user_id,
                "threshold": similarity_threshold,
                "limit": limit
            })
            
            # Convert results to list of tuples
            results = []
            for row in result:
                # Create a note-like object from the row
                note_data = {
                    "id": row.id,
                    "title": row.title,
                    "body": row.body,
                    "user_id": row.user_id,
                    "tags": row.tags,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
                similarity_score = row.similarity_score
                results.append((note_data, similarity_score))
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search on notes: {e}")
            # Fallback to empty results if vector search fails
            return []
    
    async def search_tasks(
        self,
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[Any, float]]:
        """
        Search tasks using vector similarity
        
        Args:
            db: Database session
            user_id: User ID to filter by
            query: Search query text
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of (task, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_text_embedding(query)
        
        # Perform vector similarity search using cosine similarity
        search_query = text("""
            SELECT 
                tasks.*,
                1 - (tasks.description_embedding <=> :query_embedding) AS similarity_score
            FROM tasks 
            WHERE 
                tasks.user_id = :user_id 
                AND tasks.description_embedding IS NOT NULL
                AND 1 - (tasks.description_embedding <=> :query_embedding) >= :threshold
            ORDER BY similarity_score DESC
            LIMIT :limit
        """)
        
        try:
            result = db.execute(search_query, {
                "query_embedding": query_embedding,
                "user_id": user_id,
                "threshold": similarity_threshold,
                "limit": limit
            })
            
            # Convert results to list of tuples
            results = []
            for row in result:
                # Create a task-like object from the row
                task_data = {
                    "id": row.id,
                    "description": row.description,
                    "due_date": row.due_date,
                    "is_completed": row.is_completed,
                    "user_id": row.user_id,
                    "tags": row.tags,
                    "priority": row.priority,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
                similarity_score = row.similarity_score
                results.append((task_data, similarity_score))
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search on tasks: {e}")
            # Fallback to empty results if vector search fails
            return []
    
    async def search_combined(
        self,
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> Dict[str, List[Tuple[Any, float]]]:
        """
        Search both notes and tasks using vector similarity
        
        Returns:
            Dictionary with "notes" and "tasks" keys containing search results
        """
        # Search both in parallel could be implemented here
        notes_results = await self.search_notes(
            db, user_id, query, limit, similarity_threshold
        )
        tasks_results = await self.search_tasks(
            db, user_id, query, limit, similarity_threshold
        )
        
        return {
            "notes": notes_results,
            "tasks": tasks_results
        }

class TextSearchService:
    """Service for performing traditional text-based searches"""
    
    @staticmethod
    def search_notes(
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Any]:
        """
        Search notes using traditional text search (ILIKE)
        """
        from apps.api.notes_service.app.models import Note
        
        search_pattern = f"%{query}%"
        
        return db.query(Note).filter(
            Note.user_id == user_id,
            (Note.title.ilike(search_pattern) | Note.body.ilike(search_pattern))
        ).limit(limit).all()
    
    @staticmethod
    def search_tasks(
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Any]:
        """
        Search tasks using traditional text search (ILIKE)
        """
        from apps.api.tasks_service.app.models import Task
        
        search_pattern = f"%{query}%"
        
        return db.query(Task).filter(
            Task.user_id == user_id,
            Task.description.ilike(search_pattern)
        ).limit(limit).all()
    
    @staticmethod
    def search_combined(
        db: Session,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> Dict[str, List[Any]]:
        """
        Search both notes and tasks using traditional text search
        """
        notes_results = TextSearchService.search_notes(db, user_id, query, limit)
        tasks_results = TextSearchService.search_tasks(db, user_id, query, limit)
        
        return {
            "notes": notes_results,
            "tasks": tasks_results
        }

# Global search service instances
_vector_search_service: Optional[VectorSearchService] = None
_text_search_service: Optional[TextSearchService] = None

def get_vector_search_service() -> VectorSearchService:
    """Get the global vector search service instance"""
    global _vector_search_service
    if _vector_search_service is None:
        _vector_search_service = VectorSearchService()
    return _vector_search_service

def get_text_search_service() -> TextSearchService:
    """Get the global text search service instance"""
    global _text_search_service
    if _text_search_service is None:
        _text_search_service = TextSearchService()
    return _text_search_service