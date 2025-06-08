from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from .models import Post

User = get_user_model()

class BlogAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # Создаем второго пользователя
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@example.com'
        )
        # Создаем тестовый пост
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user
        )
        # Создаем токен для авторизации
        self.access_token = jwt.encode(
            {
                'user_id': self.user.id,
                'exp': datetime.utcnow() + timedelta(minutes=60)
            },
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithm=settings.SIMPLE_JWT['ALGORITHM']
        )

    def test_list_posts(self):
        """Тест получения списка всех постов"""
        response = self.client.get('/api/blog/posts')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], 'Test Post')

    def test_get_post(self):
        """Тест получения поста по ID"""
        response = self.client.get(f'/api/blog/posts/{self.post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Test Post')
        self.assertEqual(response.json()['content'], 'Test Content')

    def test_get_nonexistent_post(self):
        """Тест получения несуществующего поста"""
        response = self.client.get('/api/blog/posts/999')
        self.assertEqual(response.status_code, 404)

    def test_create_post(self):
        """Тест создания нового поста"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        data = {
            'title': 'New Post',
            'content': 'New Content'
        }
        response = self.client.post('/api/blog/posts', data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], 'New Post')
        self.assertEqual(response.json()['content'], 'New Content')

    def test_create_post_unauthorized(self):
        """Тест создания поста без авторизации"""
        data = {
            'title': 'New Post',
            'content': 'New Content'
        }
        response = self.client.post('/api/blog/posts', data, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_update_post(self):
        """Тест обновления поста"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        data = {
            'title': 'Updated Post',
            'content': 'Updated Content'
        }
        response = self.client.put(f'/api/blog/posts/{self.post.id}', data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Updated Post')
        self.assertEqual(response.json()['content'], 'Updated Content')

    def test_update_post_unauthorized(self):
        """Тест обновления поста без авторизации"""
        data = {
            'title': 'Updated Post',
            'content': 'Updated Content'
        }
        response = self.client.put(f'/api/blog/posts/{self.post.id}', data, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_update_other_user_post(self):
        """Тест обновления чужого поста"""
        # Создаем токен для другого пользователя
        other_token = jwt.encode(
            {
                'user_id': self.other_user.id,
                'exp': datetime.utcnow() + timedelta(minutes=60)
            },
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithm=settings.SIMPLE_JWT['ALGORITHM']
        )
        headers = {'HTTP_AUTHORIZATION': f'Bearer {other_token}'}
        data = {
            'title': 'Updated Post',
            'content': 'Updated Content'
        }
        response = self.client.put(f'/api/blog/posts/{self.post.id}', data, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Вы не можете редактировать этот пост')

    def test_delete_post(self):
        """Тест удаления поста"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.delete(f'/api/blog/posts/{self.post.id}', **headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_unauthorized(self):
        """Тест удаления поста без авторизации"""
        response = self.client.delete(f'/api/blog/posts/{self.post.id}')
        self.assertEqual(response.status_code, 401)

    def test_delete_other_user_post(self):
        """Тест удаления чужого поста"""
        # Создаем токен для другого пользователя
        other_token = jwt.encode(
            {
                'user_id': self.other_user.id,
                'exp': datetime.utcnow() + timedelta(minutes=60)
            },
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithm=settings.SIMPLE_JWT['ALGORITHM']
        )
        headers = {'HTTP_AUTHORIZATION': f'Bearer {other_token}'}
        response = self.client.delete(f'/api/blog/posts/{self.post.id}', **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Вы не можете удалить этот пост')
        self.assertTrue(Post.objects.filter(id=self.post.id).exists()) 