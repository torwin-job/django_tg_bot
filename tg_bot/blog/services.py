from .models import Post
from users.models import User
from django.shortcuts import get_object_or_404
from typing import List, Dict, Any

def get_all_posts() -> List[Dict[str, Any]]:
    """
    Получение списка всех постов.
    
    Returns:
        List[Dict[str, Any]]: Список постов с информацией об авторе
    """
    posts = Post.objects.all().order_by('-created_at')
    return [
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at.isoformat()
        }
        for post in posts
    ]

def get_post_by_id(post_id: int) -> Dict[str, Any]:
    """
    Получение поста по ID.
    
    Args:
        post_id (int): ID поста
        
    Returns:
        Dict[str, Any]: Информация о посте
        
    Raises:
        Post.DoesNotExist: Если пост не найден
    """
    post = get_object_or_404(Post, id=post_id)
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat()
    }

def create_post(user_id: int, title: str, content: str) -> Dict[str, Any]:
    """
    Создание нового поста.
    
    Args:
        user_id (int): ID пользователя-автора
        title (str): Заголовок поста
        content (str): Содержание поста
        
    Returns:
        Dict[str, Any]: Созданный пост
        
    Raises:
        User.DoesNotExist: Если пользователь не найден
    """
    author = get_object_or_404(User, id=user_id)
    post = Post.objects.create(
        title=title,
        content=content,
        author=author
    )
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat()
    }

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