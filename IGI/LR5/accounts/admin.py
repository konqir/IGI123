# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Инлайн-форма для UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Тип пользователя'
    fields = ('user_type',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')

    def get_user_type(self, obj):
        return obj.user_profile.get_user_type_display() if hasattr(obj, 'user_profile') else 'Неизвестно'
    get_user_type.short_description = 'Тип пользователя'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
