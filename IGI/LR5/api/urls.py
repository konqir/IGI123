# api/urls.py
from django.urls import path
from .views import RandomUserAPIView, OpenLibraryAPIView

app_name = 'api' # Пространство имен для приложения

urlpatterns = [
    path('random_user/', RandomUserAPIView.as_view(), name='random_user'),
    path('search_books/', OpenLibraryAPIView.as_view(), name='search_books'),
]
