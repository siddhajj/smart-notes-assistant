import reflex as rx
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime, date

from .main_state import MainState

class Task(rx.Base):
    """Task model"""
    id: str = ""
    description: str = ""
    due_date: Optional[str] = None
    is_completed: bool = False
    priority: str = "medium"
    tags: List[str] = []
    created_at: str = ""
    updated_at: str = ""

class TasksState(MainState):
    """Tasks management state"""
    
    # Tasks data
    tasks: List[Task] = []
    
    # Task modal
    show_task_modal: bool = False
    
    # Form fields
    task_description: str = ""
    task_due_date: str = ""
    task_priority: str = "medium"
    task_tags: str = ""
    
    # Loading
    tasks_loading: bool = False
    task_save_loading: bool = False
    
    async def load_tasks(self):
        """Load user's tasks"""
        if not self.is_authenticated:
            return
        
        self.tasks_loading = True
        self.clear_error()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TASKS_API_URL}/tasks/",
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                tasks_data = response.json()
                
                self.tasks = [
                    Task(
                        id=str(task["id"]),
                        description=task["description"] or "",
                        due_date=task.get("due_date"),
                        is_completed=task.get("is_completed", False),
                        priority=task.get("priority", "medium"),
                        tags=task.get("tags", []) or [],
                        created_at=task["created_at"],
                        updated_at=task["updated_at"]
                    )
                    for task in tasks_data
                ]
                
                # Sort by due_date (earliest first), then by created_at
                self.tasks.sort(key=lambda x: (
                    x.due_date or "9999-12-31",  # Put tasks without due date at end
                    x.created_at
                ))
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to load tasks: {str(e)}")
        except Exception as e:
            self.set_error(f"Error loading tasks: {str(e)}")
        
        finally:
            self.tasks_loading = False
    
    def show_create_task_modal(self):
        """Show modal to create new task"""
        self.task_description = ""
        self.task_due_date = ""
        self.task_priority = "medium"
        self.task_tags = ""
        self.show_task_modal = True
    
    def close_task_modal(self):
        """Close task modal"""
        self.show_task_modal = False
        self.task_description = ""
        self.task_due_date = ""
        self.task_priority = "medium"
        self.task_tags = ""
    
    async def save_task(self):
        """Save new task"""
        if not self.task_description.strip():
            self.set_error("Task description is required")
            return
        
        self.task_save_loading = True
        self.clear_error()
        
        try:
            # Parse tags
            tags = [tag.strip() for tag in self.task_tags.split(",") if tag.strip()]
            
            task_data = {
                "description": self.task_description.strip(),
                "due_date": self.task_due_date if self.task_due_date else None,
                "priority": self.task_priority,
                "tags": tags,
                "is_completed": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.TASKS_API_URL}/tasks/",
                    json=task_data,
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                
                # Reload tasks and close modal
                await self.load_tasks()
                self.close_task_modal()
                
                return rx.toast.success("Task created successfully")
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to create task: {str(e)}")
        except Exception as e:
            self.set_error(f"Error creating task: {str(e)}")
        
        finally:
            self.task_save_loading = False
    
    async def toggle_task_completion(self, task_id: str, is_completed: bool):
        """Toggle task completion status"""
        try:
            # Find the task
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                return
            
            task_data = {
                "description": task.description,
                "due_date": task.due_date,
                "priority": task.priority,
                "tags": task.tags,
                "is_completed": is_completed
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.TASKS_API_URL}/tasks/{task_id}",
                    json=task_data,
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                
                # Update local state
                task.is_completed = is_completed
                
                status = "completed" if is_completed else "reopened"
                return rx.toast.success(f"Task {status}")
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to update task: {str(e)}")
        except Exception as e:
            self.set_error(f"Error updating task: {str(e)}")
    
    async def delete_task(self, task_id: str):
        """Delete a task"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.TASKS_API_URL}/tasks/{task_id}",
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                
                # Reload tasks
                await self.load_tasks()
                
                return rx.toast.success("Task deleted successfully")
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to delete task: {str(e)}")
        except Exception as e:
            self.set_error(f"Error deleting task: {str(e)}")
    
    def get_visible_tasks(self) -> List[Task]:
        """Get tasks that should be visible based on current settings"""
        if self.show_completed_tasks:
            return self.tasks
        else:
            return [task for task in self.tasks if not task.is_completed]
    
    def get_priority_color(self, priority: str) -> str:
        """Get color for priority level"""
        colors = {
            "low": "green",
            "medium": "blue", 
            "high": "orange",
            "urgent": "red"
        }
        return colors.get(priority, "gray")
    
    def format_due_date(self, due_date: Optional[str]) -> str:
        """Format due date for display"""
        if not due_date:
            return ""
        
        try:
            date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            today = datetime.now().date()
            task_date = date_obj.date()
            
            if task_date == today:
                return "Today"
            elif task_date == today.replace(day=today.day + 1):
                return "Tomorrow"
            else:
                return task_date.strftime("%b %d")
        except:
            return due_date