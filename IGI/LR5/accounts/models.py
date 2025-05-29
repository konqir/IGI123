# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Модель для хранения дополнительной информации о пользователе,
    включая его тип (клиент или врач).
    """
    USER_TYPE_CHOICES = [
        ('client', 'Клиент'),
        ('doctor', 'Врач'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile', primary_key=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client', verbose_name="Тип пользователя")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username} ({self.get_user_type_display()})"

