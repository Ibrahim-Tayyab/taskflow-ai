from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional


# SQLModel table that maps to the existing 'tasks' table in Neon DB
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    completed: bool = False
    category: str = "General"
    priority: str = "Medium"
    user_id: Optional[str] = None


# Pydantic models for API request/response
class TaskCreate(BaseModel):
    title: Optional[str] = None  # User-friendly title
    description: str
    completed: bool = False
    category: str = "General"
    priority: str = "Medium"


class TaskRead(BaseModel):
    id: int
    description: str
    completed: bool
    category: str
    priority: str
    user_id: Optional[str] = None


class TaskUpdate(BaseModel):
    description: Optional[str] = None
    completed: Optional[bool] = None
    category: Optional[str] = None
    priority: Optional[str] = None