import reflex as rx
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime

from .main_state import MainState

class Note(rx.Base):
    """Note model"""
    id: str = ""
    title: str = ""
    body: str = ""
    tags: List[str] = []
    created_at: str = ""
    updated_at: str = ""

class NotesState(MainState):
    """Notes management state"""
    
    # Notes data
    notes: List[Note] = []
    
    # Note modal
    show_note_modal: bool = False
    current_note: Optional[Note] = None
    note_modal_mode: str = "create"  # "create", "view", "edit"
    
    # Form fields
    note_title: str = ""
    note_body: str = ""
    note_tags: str = ""
    
    # Loading
    notes_loading: bool = False
    note_save_loading: bool = False
    
    async def load_notes(self):
        """Load user's notes"""
        if not self.is_authenticated:
            return
        
        self.notes_loading = True
        self.clear_error()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.NOTES_API_URL}/notes/",
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                notes_data = response.json()
                
                self.notes = [
                    Note(
                        id=str(note["id"]),
                        title=note["title"] or "Untitled",
                        body=note["body"] or "",
                        tags=note.get("tags", []) or [],
                        created_at=note["created_at"],
                        updated_at=note["updated_at"]
                    )
                    for note in notes_data
                ]
                
                # Sort by updated_at descending (latest first)
                self.notes.sort(key=lambda x: x.updated_at, reverse=True)
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to load notes: {str(e)}")
        except Exception as e:
            self.set_error(f"Error loading notes: {str(e)}")
        
        finally:
            self.notes_loading = False
    
    def show_create_note_modal(self):
        """Show modal to create new note"""
        self.note_modal_mode = "create"
        self.current_note = None
        self.note_title = ""
        self.note_body = ""
        self.note_tags = ""
        self.show_note_modal = True
    
    def show_view_note_modal(self, note: Note):
        """Show modal to view note"""
        self.note_modal_mode = "view"
        self.current_note = note
        self.note_title = note.title
        self.note_body = note.body
        self.note_tags = ", ".join(note.tags)
        self.show_note_modal = True
    
    def show_edit_note_modal(self, note: Note):
        """Show modal to edit note"""
        self.note_modal_mode = "edit"
        self.current_note = note
        self.note_title = note.title
        self.note_body = note.body
        self.note_tags = ", ".join(note.tags)
        self.show_note_modal = True
    
    def close_note_modal(self):
        """Close note modal"""
        self.show_note_modal = False
        self.current_note = None
        self.note_title = ""
        self.note_body = ""
        self.note_tags = ""
    
    def switch_to_edit_mode(self):
        """Switch from view to edit mode"""
        self.note_modal_mode = "edit"
    
    async def save_note(self):
        """Save note (create or update)"""
        if not self.note_title.strip():
            self.set_error("Note title is required")
            return
        
        self.note_save_loading = True
        self.clear_error()
        
        try:
            # Parse tags
            tags = [tag.strip() for tag in self.note_tags.split(",") if tag.strip()]
            
            note_data = {
                "title": self.note_title.strip(),
                "body": self.note_body.strip(),
                "tags": tags
            }
            
            async with httpx.AsyncClient() as client:
                if self.note_modal_mode == "create":
                    # Create new note
                    response = await client.post(
                        f"{self.NOTES_API_URL}/notes/",
                        json=note_data,
                        headers=self.get_auth_headers(),
                        timeout=10.0
                    )
                else:
                    # Update existing note
                    response = await client.put(
                        f"{self.NOTES_API_URL}/notes/{self.current_note.id}",
                        json=note_data,
                        headers=self.get_auth_headers(),
                        timeout=10.0
                    )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                
                # Reload notes and close modal
                await self.load_notes()
                self.close_note_modal()
                
                action = "created" if self.note_modal_mode == "create" else "updated"
                return rx.toast.success(f"Note {action} successfully")
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to save note: {str(e)}")
        except Exception as e:
            self.set_error(f"Error saving note: {str(e)}")
        
        finally:
            self.note_save_loading = False
    
    async def delete_note(self, note_id: str):
        """Delete a note"""
        self.note_save_loading = True
        self.clear_error()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.NOTES_API_URL}/notes/{note_id}",
                    headers=self.get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    await self.handle_session_expired()
                    return
                
                response.raise_for_status()
                
                # Reload notes and close modal
                await self.load_notes()
                self.close_note_modal()
                
                return rx.toast.success("Note deleted successfully")
        
        except httpx.HTTPError as e:
            self.set_error(f"Failed to delete note: {str(e)}")
        except Exception as e:
            self.set_error(f"Error deleting note: {str(e)}")
        
        finally:
            self.note_save_loading = False
    
    def get_note_preview(self, note: Note, max_length: int = 100) -> str:
        """Get preview text for a note"""
        if not note.body:
            return "No content"
        
        preview = note.body.replace("\n", " ").strip()
        if len(preview) > max_length:
            return preview[:max_length] + "..."
        return preview