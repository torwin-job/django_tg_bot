"""
URL configuration for tg_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog.api import router as blog_router
from users.api import router as users_router
from ninja import NinjaAPI
from django.conf import settings

# Создаем основной API роутер
api = NinjaAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    csrf=False
)

# Подключаем API приложений к основному роутеру
api.add_router("/users/", users_router)
api.add_router("/blog/", blog_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),  # Единый путь для всех API эндпоинтов
]
