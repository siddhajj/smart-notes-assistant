import reflex as rx
from typing import List, Dict, Any, Optional
import httpx
import asyncio

from .main_state import MainState
from .notes_state import Note
from .tasks_state import Task

class SearchResult(rx.Base):
    """Search result item"""
    id: str = ""
    title: str = ""
    content: str = ""
    type: str = ""  # "note" or "task"
    similarity_score: Optional[float] = None
    is_completed: Optional[bool] = None  # For tasks
    priority: Optional[str] = None  # For tasks
    tags: List[str] = []

class SearchState(MainState):
    """Search functionality state"""
    
    # Search query and results
    search_query: str = ""
    search_loading: bool = False
    
    # RAG results
    rag_answer: str = ""
    rag_model: str = ""
    context_used: bool = False
    
    # Grounding elements
    result_notes: List[SearchResult] = []
    result_tasks: List[SearchResult] = []
    
    # Search statistics
    total_results: int = 0
    search_type: str = ""
    
    async def perform_search(self, query: str):
        """Perform RAG search"""
        if not query.strip():
            return
        
        self.search_query = query.strip()
        self.search_loading = True
        self.clear_error()
        
        # Switch to search mode
        self.switch_to_search_mode()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.SEARCH_API_URL}/search/rag",
                    params={
                        "query": self.search_query,
                        "search_limit": 10,
                        "similarity_threshold": 0.6,
                        "use_semantic_search": True
                    },
                    headers=self.get_auth_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                search_data = response.json()
                
                # Extract RAG answer
                ai_answer = search_data.get("ai_answer", {})
                if ai_answer and ai_answer.get("success"):
                    self.rag_answer = ai_answer.get("answer", "No answer generated")
                    self.rag_model = ai_answer.get("model", "unknown")
                else:
                    self.rag_answer = "Sorry, I couldn't generate an answer for your query."
                    self.rag_model = ""
                
                self.context_used = search_data.get("context_used", False)
                self.total_results = search_data.get("total_results", 0)
                self.search_type = search_data.get("search_type", "semantic")
                
                # Process search results
                search_results = search_data.get("search_results", {})
                
                # Notes results
                notes_data = search_results.get("notes", [])
                self.result_notes = [
                    SearchResult(
                        id=note.get("id", ""),
                        title=note.get("title", "Untitled"),
                        content=note.get("body", ""),
                        type="note",
                        similarity_score=note.get("similarity_score"),
                        tags=note.get("tags", [])
                    )
                    for note in notes_data
                ]
                
                # Tasks results
                tasks_data = search_results.get("tasks", [])
                self.result_tasks = [
                    SearchResult(
                        id=task.get("id", ""),
                        title=task.get("description", ""),
                        content=task.get("description", ""),
                        type="task",
                        similarity_score=task.get("similarity_score"),
                        is_completed=task.get("is_completed", False),
                        priority=task.get("priority", "medium"),
                        tags=task.get("tags", [])
                    )
                    for task in tasks_data
                ]
        
        except httpx.HTTPError as e:
            self.set_error(f"Search failed: {str(e)}")
            self.rag_answer = "Search failed. Please try again."
        except Exception as e:
            self.set_error(f"Search error: {str(e)}")
            self.rag_answer = "An error occurred during search."
        
        finally:
            self.search_loading = False
    
    def clear_search_results(self):
        """Clear search results and return to default mode"""
        self.search_query = ""
        self.rag_answer = ""
        self.rag_model = ""
        self.context_used = False
        self.result_notes = []
        self.result_tasks = []
        self.total_results = 0
        self.search_type = ""
        self.switch_to_default_mode()
    
    def get_result_preview(self, result: SearchResult, max_length: int = 150) -> str:
        """Get preview text for a search result"""
        content = result.content or ""
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content
    
    def get_similarity_percentage(self, score: Optional[float]) -> str:
        """Convert similarity score to percentage"""
        if score is None:
            return ""
        return f"{int(score * 100)}%"
    
    def get_priority_color(self, priority: str) -> str:
        """Get color for priority level"""
        colors = {
            "low": "green",
            "medium": "blue", 
            "high": "orange",
            "urgent": "red"
        }
        return colors.get(priority, "gray")
    
    async def show_view_note_modal(self, result: SearchResult):
        """Show note modal from search result"""
        # Convert search result to note object
        from .notes_state import Note
        note = Note(
            id=result.id,
            title=result.title,
            body=result.content,
            tags=result.tags,
            created_at="",
            updated_at=""
        )
        self.show_view_note_modal(note)
    
    async def toggle_task_completion(self, task_id: str, is_completed: bool):
        """Toggle task completion from search results"""
        await super().toggle_task_completion(task_id, is_completed)
        # Refresh search results if needed
        if self.search_query:
            await self.perform_search(self.search_query)
    
    async def delete_task(self, task_id: str):
        """Delete task from search results"""
        await super().delete_task(task_id)
        # Refresh search results if needed
        if self.search_query:
            await self.perform_search(self.search_query)