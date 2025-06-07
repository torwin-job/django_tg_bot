from ninja import Schema
from .models import User

class UserSchema(Schema):
    id: int
    username: str
    email: str

    class Config:
        model = User
        model_fields = ['id', 'username', 'email']

class UserCreateSchema(Schema):
    username: str
    password: str
    email: str

class LoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access: str
    refresh: str

class ErrorSchema(Schema):
    detail: str 

class RefreshSchema(Schema):
    refresh: str
