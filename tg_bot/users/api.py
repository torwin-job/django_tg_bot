from ninja import Router, Schema
from ninja.security import HttpBearer
from .models import User
from .services import create_user, authenticate_user, get_user_by_id
from django.conf import settings
import jwt
from .schemas import UserSchema, UserCreateSchema, LoginSchema, TokenSchema, ErrorSchema, RefreshSchema
from django.contrib.auth import authenticate
from typing import Optional
from datetime import datetime, timedelta


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = payload.get('user_id')
            if user_id:
                return user_id
        except:
            pass
        return None

# Создаем роутер вместо API
router = Router(auth=AuthBearer(), tags=["Пользователи"])

@router.post("/register", response={201: UserSchema, 400: ErrorSchema}, auth=None, summary="Регистрация нового пользователя")
def register(request, data: UserCreateSchema):
    """
    Регистрация нового пользователя.
    
    - **username**: Имя пользователя
    - **password**: Пароль
    - **email**: Email адрес
    
    Возвращает данные созданного пользователя.
    """
    try:
        user = create_user(data.username, data.password, data.email)
        return 201, {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    except Exception as e:
        return 400, {"detail": str(e)}

@router.post("/login", response={200: TokenSchema, 401: ErrorSchema}, auth=None, summary="Авторизация пользователя")
def login(request, payload: LoginSchema):
    """
    Авторизация пользователя.
    
    Args:
    - **username**: Имя пользователя
    - **password**: Пароль
    
    Returns:
    - **access**: JWT токен доступа
    - **refresh**: JWT токен обновления
    """
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        return 401, {"detail": "Неверные учетные данные"}
    
    # Создаем токены
    access_token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        },
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithm=settings.SIMPLE_JWT['ALGORITHM']
    )
    
    refresh_token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        },
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithm=settings.SIMPLE_JWT['ALGORITHM']
    )
    
    return 200, {
        "access": access_token,
        "refresh": refresh_token
    }

@router.post("/refresh", response={200: TokenSchema, 400: ErrorSchema}, auth=None, summary="Обновление токена")
def refresh_token(request, data: RefreshSchema):
    """
    Обновление токена доступа.
    
    - **refresh**: Токен обновления
    
    Возвращает новые JWT токены.
    """
    try:
        payload = jwt.decode(data.refresh, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        user_id = payload.get('user_id')
        if not user_id:
            raise Exception("Недействительный токен")
        
        user = get_user_by_id(user_id)
        if not user:
            raise Exception("Пользователь не найден")
        
        access_token = jwt.encode(
            {'user_id': user.id},
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithm=settings.SIMPLE_JWT['ALGORITHM']
        )
        
        refresh_token = jwt.encode(
            {'user_id': user.id},
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithm=settings.SIMPLE_JWT['ALGORITHM']
        )
        
        return 200, {
            'access': access_token,
            'refresh': refresh_token
        }
    except Exception as e:
        return 400, {"detail": str(e)}

@router.get("/me", response={200: UserSchema, 401: ErrorSchema}, summary="Информация о текущем пользователе")
def get_current_user(request):
    """
    Получение информации о текущем пользователе.
    
    Требуется аутентификация.
    
    Возвращает данные пользователя:
    - **id**: ID пользователя
    - **username**: Имя пользователя
    - **email**: Email адрес
    """
    try:
        user = get_user_by_id(request.auth)
        return 200, user
    except Exception as e:
        return 401, {"detail": str(e)} 