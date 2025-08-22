import reflex as rx
from typing import Dict, Any, List, Optional
import asyncio
import httpx
import os

class MainState(rx.State):
    """Main application state"""
    
    # Authentication
    is_authenticated: bool = False
    user_id: str = ""
    username: str = ""
    access_token: str = ""
    
    # UI Mode
    current_mode: str = "default"  # "default" or "search"
    
    # Panel visibility
    notes_expanded: bool = False
    tasks_expanded: bool = False
    show_completed_tasks: bool = False
    
    # Loading states
    is_loading: bool = False
    error_message: str = ""
    
    # API URLs
    NOTES_API_URL: str = os.getenv("NOTES_SERVICE_URL", "http://localhost:8000")
    TASKS_API_URL: str = os.getenv("TASKS_SERVICE_URL", "http://localhost:8002")
    SEARCH_API_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8004")
    
    def set_authenticated(self, user_data: Dict[str, Any]):
        """Set user as authenticated"""
        self.is_authenticated = True
        self.user_id = user_data.get("user_id", "")
        self.username = user_data.get("username", "")
        self.access_token = user_data.get("access_token", "")
    
    def logout(self):
        """Logout user and reset state"""
        self.is_authenticated = False
        self.user_id = ""
        self.username = ""
        self.access_token = ""
        self.current_mode = "default"
        self.notes_expanded = False
        self.tasks_expanded = False
        self.error_message = ""
        return rx.toast.info("Logged out successfully")
    
    def switch_to_search_mode(self):
        """Switch to search results view"""
        self.current_mode = "search"
        self.notes_expanded = False
        self.tasks_expanded = False
    
    def switch_to_default_mode(self):
        """Switch back to notes/tasks view"""
        self.current_mode = "default"
    
    def expand_notes(self):
        """Expand notes panel to full width"""
        self.notes_expanded = True
        self.tasks_expanded = False
    
    def expand_tasks(self):
        """Expand tasks panel to full width"""
        self.tasks_expanded = True
        self.notes_expanded = False
    
    def reset_panels(self):
        """Reset panels to default 50/50 split"""
        self.notes_expanded = False
        self.tasks_expanded = False
    
    def toggle_completed_tasks(self):
        """Toggle visibility of completed tasks"""
        self.show_completed_tasks = not self.show_completed_tasks
    
    def set_error(self, message: str):
        """Set error message"""
        self.error_message = message
        return rx.toast.error(message)
    
    def clear_error(self):
        """Clear error message"""
        self.error_message = ""
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API calls"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    async def check_authentication(self):
        """Check if user is still authenticated"""
        if not self.access_token:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.NOTES_API_URL}/",
                    headers=self.get_auth_headers(),
                    timeout=5.0
                )
                return response.status_code != 401
        except:
            return False
    
    async def handle_session_expired(self):
        """Handle session expiration"""
        self.logout()
        self.error_message = "Your session has expired. Please log in again."
        return rx.toast.warning("Session expired. Please log in again.")