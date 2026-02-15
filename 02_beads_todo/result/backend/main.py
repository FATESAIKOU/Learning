from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

class TodoIn(BaseModel):
    title: str
    status: Optional[str] = "pending"

class Todo(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Basic In-Memory store for now, will replace with DB in Step 03
fake_db = []

@app.get("/")
def read_root():
    return {"message": "Hello Beads!"}

@app.get("/todos", response_model=List[Todo])
def get_todos():
    return fake_db

@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoIn):
    new_todo = Todo(
        id=len(fake_db) + 1,
        title=todo.title,
        status=todo.status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    fake_db.append(new_todo)
    return new_todo
