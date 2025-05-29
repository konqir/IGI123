# accounts/urls.py
from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, ProfileView

app_name = 'accounts' # Пространство имен для приложения

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'), # Страница входа
    path('logout/', CustomLogoutView.as_view(), name='logout'), # Выход из системы
    path('register/', RegisterView.as_view(), name='register'), # Страница регистрации
    path('profile/', ProfileView.as_view(), name='profile'), # Страница профиля
]
