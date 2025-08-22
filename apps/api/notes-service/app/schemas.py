from pydantic import BaseModel
from typing import Optional

class NoteCreate(BaseModel):
    title: str
    body: Optional[str] = None

class NoteResponse(BaseModel):
    id: str
    title: str
    body: Optional[str] = None
    user_id: str

    class Config:
        orm_mode = True
