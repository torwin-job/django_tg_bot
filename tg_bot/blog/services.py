from .models import Post
from users.models import User
from django.shortcuts import get_object_or_404
from typing import List, Dict, Any

def get_all_posts():
    """Получение всех постов с предзагрузкой автора"""
    return list(Post.objects.select_related('author').all())

def get_post_by_id(post_id):
    """Получение поста по ID с предзагрузкой автора"""
    return Post.objects.select_related('author').get(id=post_id)

def create_post(author_id, title, content):
    """Создание нового поста"""
    return Post.objects.create(
        author_id=author_id,
        title=title,
        content=content
    )

def update_post(post_id: int, user_id: int, title: str = None, content: str = None) -> Dict[str, Any]:
    """
    Обновление существующего поста.
    
    Args:
        post_id (int): ID поста
        user_id (int): ID пользователя
        title (str, optional): Новый заголовок
        content (str, optional): Новое содержание
        
    Returns:
        Dict[str, Any]: Обновленный пост
        
    Raises:
        Post.DoesNotExist: Если пост не найден
        PermissionError: Если пользователь не является автором поста
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author.id != user_id:
        raise PermissionError("Вы не можете редактировать этот пост")
    
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    
    post.save()
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat()
    }

def delete_post(post_id: int, user_id: int) -> None:
    """
    Удаление поста.
    
    Args:
        post_id (int): ID поста
        user_id (int): ID пользователя
        
    Raises:
        Post.DoesNotExist: Если пост не найден
        PermissionError: Если пользователь не является автором поста
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author.id != user_id:
        raise PermissionError("Вы не можете удалить этот пост")
    
    post.delete() 