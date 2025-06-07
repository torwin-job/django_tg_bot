from ninja import Router, Schema
from ninja.security import HttpBearer
from .models import Post
from .services import get_all_posts, get_post_by_id, create_post, update_post, delete_post
from django.conf import settings
import jwt
from typing import List, Optional

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

class PostSchema(Schema):
    id: int
    title: str
    content: str
    author: str
    created_at: str

    class Config:
        model = Post
        model_fields = ['id', 'title', 'content', 'author', 'created_at']

class PostCreateSchema(Schema):
    title: str
    content: str

class PostUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None

class ErrorSchema(Schema):
    detail: str

# Создаем роутер вместо API
router = Router(auth=AuthBearer(), tags=["Блог"])

@router.get("/posts", response={200: List[PostSchema]}, auth=None, summary="Список всех постов")
def list_posts(request):
    """
    Получение списка всех постов.
    
    Возвращает массив постов с полями:
    - **id**: ID поста
    - **title**: Заголовок
    - **content**: Содержание
    - **author**: Имя автора
    - **created_at**: Дата создания
    """
    return 200, get_all_posts()

@router.get("/posts/{post_id}", response={200: PostSchema, 404: ErrorSchema}, auth=None, summary="Получение поста по ID")
def get_post(request, post_id: int):
    """
    Получение информации о конкретном посте.
    
    - **post_id**: ID поста
    
    Возвращает:
    - **id**: ID поста
    - **title**: Заголовок
    - **content**: Содержание
    - **author**: Имя автора
    - **created_at**: Дата создания
    """
    try:
        post = get_post_by_id(post_id)
        return 200, post
    except Post.DoesNotExist:
        return 404, {"detail": "Пост не найден"}

@router.post("/posts", response={201: PostSchema, 400: ErrorSchema}, summary="Создание нового поста")
def create_new_post(request, data: PostCreateSchema):
    """
    Создание нового поста.
    
    Требуется аутентификация.
    
    - **title**: Заголовок поста
    - **content**: Содержание поста
    
    Возвращает созданный пост.
    """
    try:
        post = create_post(request.auth, data.title, data.content)
        return 201, post
    except Exception as e:
        return 400, {"detail": str(e)}

@router.put("/posts/{post_id}", response={200: PostSchema, 400: ErrorSchema, 404: ErrorSchema}, summary="Обновление поста")
def update_existing_post(request, post_id: int, data: PostUpdateSchema):
    """
    Обновление существующего поста.
    
    Требуется аутентификация.
    Только автор может обновлять свой пост.
    
    - **post_id**: ID поста
    - **title**: Новый заголовок (опционально)
    - **content**: Новое содержание (опционально)
    
    Возвращает обновленный пост.
    """
    try:
        post = update_post(post_id, request.auth, data.title, data.content)
        return 200, post
    except Post.DoesNotExist:
        return 404, {"detail": "Пост не найден"}
    except Exception as e:
        return 400, {"detail": str(e)}

@router.delete("/posts/{post_id}", response={204: None, 400: ErrorSchema, 404: ErrorSchema}, summary="Удаление поста")
def delete_existing_post(request, post_id: int):
    """
    Удаление поста.
    
    Требуется аутентификация.
    Только автор может удалять свой пост.
    
    - **post_id**: ID поста
    
    Возвращает 204 при успешном удалении.
    """
    try:
        delete_post(post_id, request.auth)
        return 204, None
    except Post.DoesNotExist:
        return 404, {"detail": "Пост не найден"}
    except Exception as e:
        return 400, {"detail": str(e)}

