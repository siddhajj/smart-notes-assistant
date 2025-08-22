from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import httpx
import os
import logging

from apps.api.shared.search import get_vector_search_service, get_text_search_service

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval Augmented Generation service for enhanced search and question answering"""
    
    def __init__(self):
        self.vector_search = get_vector_search_service()
        self.text_search = get_text_search_service()
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
    
    async def search_and_answer(
        self,
        db: Session,
        user_id: str,
        query: str,
        search_limit: int = 5,
        similarity_threshold: float = 0.7,
        use_semantic_search: bool = True
    ) -> Dict[str, Any]:
        """
        Perform RAG: search for relevant content and generate an AI-powered answer
        
        Args:
            db: Database session
            user_id: User ID to filter by
            query: User question/query
            search_limit: Number of search results to use as context
            similarity_threshold: Minimum similarity for semantic search
            use_semantic_search: Whether to use semantic or text search
        
        Returns:
            Dictionary with search results, generated answer, and metadata
        """
        
        # Step 1: Retrieve relevant content
        if use_semantic_search:
            search_results = await self._semantic_search_combined(
                db, user_id, query, search_limit, similarity_threshold
            )
        else:
            search_results = self._text_search_combined(
                db, user_id, query, search_limit
            )
        
        # Step 2: Format context for AI
        context = self._format_context_for_ai(search_results, query)
        
        # Step 3: Generate AI answer if we have relevant content
        ai_answer = None
        if context["has_content"]:
            ai_answer = await self._generate_ai_answer(query, context["formatted_context"])
        
        # Step 4: Return comprehensive results
        return {
            "query": query,
            "search_results": search_results,
            "ai_answer": ai_answer,
            "context_used": context["has_content"],
            "search_type": "semantic" if use_semantic_search else "text",
            "total_results": len(search_results.get("notes", [])) + len(search_results.get("tasks", [])),
            "metadata": {
                "similarity_threshold": similarity_threshold if use_semantic_search else None,
                "search_limit": search_limit
            }
        }
    
    async def _semantic_search_combined(
        self,
        db: Session,
        user_id: str,
        query: str,
        limit: int,
        similarity_threshold: float
    ) -> Dict[str, List[Any]]:
        """Perform semantic search across notes and tasks"""
        results = await self.vector_search.search_combined(
            db, user_id, query, limit, similarity_threshold
        )
        
        # Format results consistently
        return {
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
    
    def _text_search_combined(
        self,
        db: Session,
        user_id: str,
        query: str,
        limit: int
    ) -> Dict[str, List[Any]]:
        """Perform text search across notes and tasks"""
        results = self.text_search.search_combined(db, user_id, query, limit)
        
        # Format results consistently
        return {
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
    
    def _format_context_for_ai(self, search_results: Dict[str, List[Any]], query: str) -> Dict[str, Any]:
        """Format search results into context for AI generation"""
        
        notes = search_results.get("notes", [])
        tasks = search_results.get("tasks", [])
        
        if not notes and not tasks:
            return {"has_content": False, "formatted_context": ""}
        
        context_parts = []
        
        # Add notes context
        if notes:
            context_parts.append("=== NOTES ===")
            for i, note in enumerate(notes[:3], 1):  # Limit to top 3 notes
                similarity_info = f" (similarity: {note.get('similarity_score', 'N/A')})" if 'similarity_score' in note else ""
                context_parts.append(f"Note {i}{similarity_info}:")
                context_parts.append(f"Title: {note['title']}")
                context_parts.append(f"Content: {note['body'][:500]}...")  # Truncate long content
                if note.get('tags'):
                    context_parts.append(f"Tags: {', '.join(note['tags'])}")
                context_parts.append("")
        
        # Add tasks context
        if tasks:
            context_parts.append("=== TASKS ===")
            for i, task in enumerate(tasks[:3], 1):  # Limit to top 3 tasks
                similarity_info = f" (similarity: {task.get('similarity_score', 'N/A')})" if 'similarity_score' in task else ""
                context_parts.append(f"Task {i}{similarity_info}:")
                context_parts.append(f"Description: {task['description']}")
                context_parts.append(f"Status: {'Completed' if task['is_completed'] else 'Pending'}")
                context_parts.append(f"Priority: {task['priority']}")
                if task.get('due_date'):
                    context_parts.append(f"Due Date: {task['due_date']}")
                if task.get('tags'):
                    context_parts.append(f"Tags: {', '.join(task['tags'])}")
                context_parts.append("")
        
        formatted_context = "\n".join(context_parts)
        
        return {
            "has_content": True,
            "formatted_context": formatted_context
        }
    
    async def _generate_ai_answer(self, query: str, context: str) -> Optional[Dict[str, Any]]:
        """Generate AI answer using the retrieved context"""
        
        try:
            # Prepare the prompt for the AI service
            system_prompt = """You are a helpful assistant that answers questions based on a user's notes and tasks. 
Use only the provided context to answer questions. If the context doesn't contain enough information to answer 
the question, say so clearly. Be concise but helpful, and reference specific notes or tasks when relevant."""
            
            user_prompt = f"""Based on the following context from the user's notes and tasks, please answer this question: "{query}"

Context:
{context}

Please provide a helpful answer based only on the information provided in the context above."""
            
            # Call AI service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_service_url}/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    ai_response = response.json()
                    return {
                        "answer": ai_response.get("response", "").strip(),
                        "success": True,
                        "model": ai_response.get("model", "unknown")
                    }
                else:
                    logger.warning(f"AI service returned status {response.status_code}")
                    return {
                        "answer": "Sorry, I couldn't generate an answer at this time.",
                        "success": False,
                        "error": f"AI service error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating AI answer: {e}")
            return {
                "answer": "Sorry, I couldn't generate an answer due to a technical issue.",
                "success": False,
                "error": str(e)
            }
    
    async def ask_question(
        self,
        db: Session,
        user_id: str,
        question: str,
        search_type: str = "semantic",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Ask a question about the user's notes and tasks using RAG
        
        This is a convenience method that provides a simpler interface for Q&A
        """
        use_semantic = search_type.lower() == "semantic"
        
        return await self.search_and_answer(
            db=db,
            user_id=user_id,
            query=question,
            search_limit=limit,
            use_semantic_search=use_semantic
        )

# Global RAG service instance
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """Get the global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service