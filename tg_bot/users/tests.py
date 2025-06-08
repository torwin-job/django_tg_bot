from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from datetime import datetime, timedelta

User = get_user_model()

class UserAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        self.user = User.objects.create_user(
            username=self.test_user['username'],
            password=self.test_user['password'],
            email=self.test_user['email']
        )

    def test_register_user(self):
        """Тест регистрации нового пользователя"""
        new_user = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/users/register', new_user, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        """Тест регистрации с существующим именем пользователя"""
        response = self.client.post('/api/users/register', self.test_user, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        """Тест успешной авторизации"""
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self.client.post('/api/users/login', login_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_login_wrong_credentials(self):
        """Тест авторизации с неверными данными"""
        login_data = {
            'username': self.test_user['username'],
            'password': 'wrongpass'
        }
        response = self.client.post('/api/users/login', login_data, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_refresh_token(self):
        """Тест обновления токена"""
        # Сначала получаем токены через логин
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        login_response = self.client.post('/api/users/login', login_data, content_type='application/json')
        refresh_token = login_response.json()['refresh']

        # Тестируем обновление токена
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/users/refresh', refresh_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_get_current_user(self):
        """Тест получения информации о текущем пользователе"""
        # Получаем токен через логин
        login_data = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        login_response = self.client.post('/api/users/login', login_data, content_type='application/json')
        access_token = login_response.json()['access']

        # Тестируем получение информации о пользователе
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        response = self.client.get('/api/users/me', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], self.test_user['username'])
        self.assertEqual(response.json()['email'], self.test_user['email'])

    def test_get_current_user_unauthorized(self):
        """Тест получения информации о пользователе без авторизации"""
        response = self.client.get('/api/users/me')
        self.assertEqual(response.status_code, 401) 