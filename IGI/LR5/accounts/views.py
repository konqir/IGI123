# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
import datetime
from django.utils import timezone
from .models import UserProfile
from .forms import UserUpdateForm, ClientUpdateForm, UserRegistrationForm
from core.models import Client

# Инициализация логгера для приложения accounts
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    """
    Кастомизированное представление для входа пользователя.
    Использует встроенный LoginView Django.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True # Перенаправлять аутентифицированных пользователей

    def get_success_url(self):
        logger.info(f"Пользователь {self.request.user.username} успешно вошел в систему.")
        messages.success(self.request, f"Добро пожаловать, {self.request.user.username}!")
        return reverse_lazy('core:home')

    def form_invalid(self, form):
        logger.warning(f"Неудачная попытка входа для пользователя: {form.data.get('username')}")
        messages.error(self.request, "Неверное имя пользователя или пароль.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Кастомизированное представление для выхода пользователя.
    """
    next_page = reverse_lazy('core:home') # Перенаправляем на главную страницу после выхода


class RegisterView(CreateView):
    """
    Представление для регистрации нового пользователя.
    Использует кастомизированную UserRegistrationForm.
    """
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()

        # Создаем или обновляем объект UserProfile для нового пользователя.
        # По умолчанию user_type будет 'client'.
        user_profile, created_profile = UserProfile.objects.get_or_create(user=user)
        if created_profile:
            logger.info(f"Создан новый UserProfile для пользователя {user.username} с типом '{user_profile.user_type}'.")
        else:
            logger.info(f"UserProfile для пользователя {user.username} уже существовал (Тип: {user_profile.user_type}).")

        client, created = Client.objects.update_or_create(
            user=user,
            defaults={
                'phone_number': form.cleaned_data['phone_number'],
                'address': form.cleaned_data['address'],
                'date_of_birth': form.cleaned_data['date_of_birth']
            }
        )
        if created:
            logger.info(f"Создан новый объект Client для пользователя {user.username}.")
        else:
            logger.info(f"Обновлен существующий объект Client для пользователя {user.username}.")

        messages.success(self.request, 'Ваш аккаунт успешно создан! Теперь вы можете войти.')
        logger.info(f"Новый пользователь {user.username} успешно зарегистрирован.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Если форма недействительна, рендерим форму с ошибками.
        Возвращаем результат вызова super().form_invalid(form),
        чтобы Django сам обработал рендеринг шаблона с ошибками.
        """
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
        logger.warning(f"Ошибка при регистрации нового пользователя: {form.errors}")
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    Представление для просмотра и редактирования профиля пользователя.
    Отображает формы для User и Client.
    """
    model = Client
    form_class = ClientUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        """
        Получаем объект Client, связанный с текущим пользователем.
        Если Client не существует, создаем его с допустимым значением по умолчанию для date_of_birth.
        """
        try:
            client = Client.objects.get(user=self.request.user)
        except Client.DoesNotExist:
            # Если Client не существует, создаем его с значениями по умолчанию.
            default_date_of_birth = timezone.localdate() - datetime.timedelta(days=20 * 365 + 5)
            client = Client.objects.create(
                user=self.request.user,
                phone_number='',
                address='',
                date_of_birth=default_date_of_birth
            )
            logger.info(f"Создан новый объект Client для пользователя {self.request.user.username} с датой рождения по умолчанию.")
            messages.info(self.request, "Ваш профиль был инициализирован. Пожалуйста, обновите информацию.")
        return client

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем форму для User, если она еще не была создана
        if 'user_form' not in context:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        logger.info(f"Загружена страница профиля для пользователя {self.request.user.username}.")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        user_form = UserUpdateForm(request.POST, instance=request.user)
        client_form = ClientUpdateForm(request.POST, instance=self.object)

        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            logger.info(f"Профиль пользователя {request.user.username} успешно обновлен.")
            return redirect(self.get_success_url())
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            logger.warning(f"Ошибка при обновлении профиля пользователя {request.user.username}: {user_form.errors} | {client_form.errors}")
            # Если формы невалидны, передаем их в контекст для отображения ошибок
            context = self.get_context_data(object=self.object)
            context['user_form'] = user_form
            context['form'] = client_form
            return render(request, self.template_name, context)

