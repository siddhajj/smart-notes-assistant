from pydantic import BaseModel
from typing import Optional
from datetime import date

class TaskCreate(BaseModel):
    description: str
    due_date: Optional[date] = None

class TaskResponse(BaseModel):
    id: str
    description: str
    due_date: Optional[date] = None
    is_completed: bool
    user_id: str

    class Config:
        orm_mode = True
