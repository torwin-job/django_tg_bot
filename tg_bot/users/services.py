from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from typing import Optional, Dict, Any

User = get_user_model()

def create_user(username: str, password: str, email: str) -> User:
    """
    Создает нового пользователя с указанными данными.
    """
    if User.objects.filter(username=username).exists():
        raise ValueError("Пользователь с таким именем уже существует")
    
    if User.objects.filter(email=email).exists():
        raise ValueError("Пользователь с таким email уже существует")
    
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        is_active=True  # Убеждаемся, что пользователь активен
    )
    return user

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по имени пользователя и паролю.
    """
    try:
        user = User.objects.get(username=username)
        if user.check_password(password) and user.is_active:
            return user
    except User.DoesNotExist:
        pass
    return None

def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Получает пользователя по его ID.
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None 