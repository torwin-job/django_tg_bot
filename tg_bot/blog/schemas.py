from ninja import Schema
from datetime import datetime

class PostSchema(Schema):
    id: int
    title: str
    content: str
    created_at: datetime
    author: str

    class Config:
        orm_mode = True
        from_attributes = True

class PostCreateSchema(Schema):
    title: str
    content: str 