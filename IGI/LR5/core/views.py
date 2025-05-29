# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
import logging
import datetime
import calendar
from decimal import Decimal
import requests
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json
from collections import Counter

from .models import (
    CompanyInfo, FAQ, Vacancy, Doctor, Service, Client, DoctorCategory,
    Appointment, Review, PromoCode, ServiceCategory, AppointmentService,
    Schedule, NewsArticle, Room
)
from accounts.models import UserProfile
from .forms import ReviewForm, AppointmentForm, ServiceForm

# Инициализация логгера для приложения core
logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    """
    Представление для главной страницы.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем последнюю новостную статью
        try:
            context['latest_article'] = NewsArticle.objects.latest('published_date')
            logger.info("На главную страницу загружена последняя новостная статья.")
        except NewsArticle.DoesNotExist:
            context['latest_article'] = None
            logger.info("На главной странице нет новостных статей.")
        return context

class CompanyInfoView(TemplateView):
    """
    Представление для страницы "О компании".
    """
    template_name = 'company_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем информацию о компании, если она существует
        context['company_info'] = CompanyInfo.objects.first()
        logger.info("Загружена страница 'О компании'.")
        return context


class FAQListView(ListView):
    """
    Представление для списка часто задаваемых вопросов (FAQ).
    """
    model = FAQ
    template_name = 'faq_list.html'
    context_object_name = 'faqs'
    paginate_by = 10

    def get_queryset(self):
        logger.info("Загружен список FAQ.")
        return FAQ.objects.all()


class ContactView(ListView):
    """
    Представление для страницы контактов, отображает список врачей.
    """
    model = Doctor
    template_name = 'contacts.html'
    context_object_name = 'doctors'
    paginate_by = 9

    def get_queryset(self):
        logger.info("Загружен список врачей на странице контактов.")
        return Doctor.objects.all()


class PrivacyPolicyView(TemplateView):
    """
    Представление для страницы политики конфиденциальности.
    """
    template_name = 'privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("Загружена страница политики конфиденциальности.")
        return context


class VacancyListView(ListView):
    """
    Представление для списка вакансий.
    """
    model = Vacancy
    template_name = 'vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10

    def get_queryset(self):
        logger.info("Загружен список вакансий.")
        return Vacancy.objects.filter(is_active=True) # Отображаем только активные вакансии


class ReviewListView(ListView):
    """
    Представление для списка отзывов.
    """
    model = Review
    template_name = 'review_list.html'
    context_object_name = 'reviews'
    paginate_by = 5

    def get_queryset(self):
        logger.info("Загружен список отзывов.")
        return Review.objects.all()


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового отзыва.
    Требует аутентификации.
    """
    model = Review
    form_class = ReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('core:review_list')

    def form_valid(self, form):
        form.instance.client = self.request.user.client_profile
        response = super().form_valid(form)
        messages.success(self.request, 'Ваш отзыв успешно добавлен!')
        logger.info(f"Новый отзыв добавлен пользователем {self.request.user.username}.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("Загружена форма добавления отзыва.")
        return context


class PromoCodeListView(ListView):
    """
    Представление для списка активных промокодов.
    """
    model = PromoCode
    template_name = 'promo_code_list.html'
    context_object_name = 'promo_codes'

    def get_queryset(self):
        # Получаем только активные промокоды, срок действия которых не истек
        queryset = PromoCode.objects.filter(is_active=True).filter(
            Q(expiration_date__isnull=True) | Q(expiration_date__gte=timezone.localdate())
        )
        logger.info("Загружен список промокодов.")
        return queryset


class ServiceListView(ListView):
    """
    Представление для списка услуг с фильтрацией, поиском и сортировкой.
    """
    model = Service
    template_name = 'service_list.html'
    context_object_name = 'services'
    paginate_by = 9

    def get_queryset(self):
        queryset = Service.objects.all()
        
        # Фильтрация по категории
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # Фильтрация по цене
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except:
                pass # Пропускаем, если невалидное значение
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except:
                pass # Пропускаем, если невалидное значение

        # Поиск по названию или описанию
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        # Сортировка
        sort_by = self.request.GET.get('sort_by', 'name') # По умолчанию сортируем по названию
        if sort_by in ['name', 'price', '-price', 'duration_minutes', '-duration_minutes']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('name')
        logger.info(f"Загружен список услуг с фильтрами: {self.request.GET}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_search_query'] = self.request.GET.get('q', '')
        context['current_sort_by'] = self.request.GET.get('sort_by', 'name')
        return context


class ServiceDetailView(DetailView):
    """
    Представление для детального просмотра услуги.
    """
    model = Service
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f"Загружена детальная страница услуги: {self.object.name}.")
        return context


class ServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Представление для создания новой услуги.
    Доступно только суперпользователям.
    """
    model = Service
    form_class = ServiceForm
    template_name = 'service_form.html'
    success_url = reverse_lazy('core:service_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Добавить новую услугу"
        logger.info("Загружена форма добавления услуги.")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Услуга успешно добавлена!')
        logger.info(f"Услуга '{self.object.name}' добавлена суперпользователем {self.request.user.username}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        logger.warning(f"Ошибка при добавлении услуги: {form.errors}")
        return super().form_invalid(form)


class ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление для редактирования существующей услуги.
    Доступно только суперпользователям.
    """
    model = Service
    form_class = ServiceForm
    template_name = 'service_form.html'
    success_url = reverse_lazy('core:service_list')
    context_object_name = 'service'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Редактировать услугу"
        logger.info(f"Загружена форма редактирования услуги: {self.object.name}.")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Услуга успешно обновлена!')
        logger.info(f"Услуга '{self.object.name}' обновлена суперпользователем {self.request.user.username}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        logger.warning(f"Ошибка при обновлении услуги: {form.errors}")
        return super().form_invalid(form)


class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Представление для удаления услуги.
    Доступно только суперпользователям.
    """
    model = Service
    template_name = 'service_confirm_delete.html'
    success_url = reverse_lazy('core:service_list')
    context_object_name = 'service'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Удалить услугу"
        logger.info(f"Загружена страница подтверждения удаления услуги: {self.object.name}.")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Услуга успешно удалена!')
        logger.info(f"Услуга '{self.object.name}' удалена суперпользователем {self.request.user.username}.")
        return response


class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Представление для отображения статистики.
    Доступно только суперпользователям.
    """
    template_name = 'statistics.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- Общая сумма продаж ---
        total_sales = Appointment.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
        context['total_sales'] = total_sales

        # --- Список клиентов в алфавитном порядке ---
        clients_with_appointments = Client.objects.filter(appointments__isnull=False).distinct().order_by('user__first_name', 'user__last_name')
        context['clients_alphabetical'] = clients_with_appointments

        # --- Список услуг/товаров в алфавитном порядке ---
        services_alphabetical = Service.objects.all().order_by('name')
        context['services_alphabetical'] = services_alphabetical

        # --- Статистические показатели по сумме продаж ---
        completed_appointments_prices = Appointment.objects.filter(status='completed').values_list('total_price', flat=True)
        prices_list = [float(price) for price in completed_appointments_prices if price is not None]

        context['sales_mean'] = sum(prices_list) / len(prices_list) if prices_list else 0
        
        if prices_list:
            data_counts = Counter(prices_list)
            max_count = 0
            modes = []
            for value, count in data_counts.items():
                if count > max_count:
                    max_count = count
                    modes = [value]
                elif count == max_count:
                    modes.append(value)
            context['sales_mode'] = sorted(list(set(modes)))
        else:
            context['sales_mode'] = []

        if prices_list:
            sorted_prices = sorted(prices_list)
            mid = len(sorted_prices) // 2
            if len(sorted_prices) % 2 == 0:
                context['sales_median'] = (sorted_prices[mid - 1] + sorted_prices[mid]) / 2
            else:
                context['sales_median'] = sorted_prices[mid]
        else:
            context['sales_median'] = 0

        # --- Статистические показатели по возрасту клиентов ---
        clients_dob = Client.objects.exclude(date_of_birth__isnull=True).values_list('date_of_birth', flat=True)
        ages = []
        for dob in clients_dob:
            today = timezone.localdate()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            ages.append(age)

        context['client_age_mean'] = sum(ages) / len(ages) if ages else 0
        if ages:
            sorted_ages = sorted(ages)
            mid = len(sorted_ages) // 2
            if len(sorted_ages) % 2 == 0:
                context['client_age_median'] = (sorted_ages[mid - 1] + sorted_ages[mid]) / 2
            else:
                context['client_age_median'] = sorted_ages[mid]
        else:
            context['client_age_median'] = 0

        # --- Какой тип товаров наиболее популярен? (по количеству записей, включая запланированные) ---
        popular_service_types = Appointment.objects.filter(
            service__isnull=False, status__in=['completed', 'planned']
        ).values('service__category__name').annotate(
            count=Count('service__category')
        ).order_by('-count')[:5]
        context['popular_service_types'] = popular_service_types

        # --- Какой тип товаров приносит наибольшую прибыль? ---
        profitable_service_types = Appointment.objects.filter(
            service__isnull=False, status='completed'
        ).values('service__category__name').annotate(
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')[:5]
        context['profitable_service_types'] = profitable_service_types

        # --- Данные для графика: Загруженность кабинетов (по количеству записей за последние 6 месяцев) ---
        room_labels = []
        room_appointment_counts = []

        six_months_ago = timezone.localdate() - datetime.timedelta(days=6 * 30) 
        
        # Получаем все записи за последние 6 месяцев
        recent_appointments = Appointment.objects.filter(
            date__gte=six_months_ago
        ).select_related('doctor')

        room_counts = Counter()
        for appt in recent_appointments:
            matching_schedule = Schedule.objects.filter(
                doctor=appt.doctor,
                date=appt.date,
                start_time__lte=appt.start_time,
                end_time__gte=appt.end_time
            ).first()

            if matching_schedule and matching_schedule.room:
                room_counts[matching_schedule.room.name] += 1
        
        # Получаем все существующие кабинеты, чтобы отобразить их, даже если у них 0 записей
        all_rooms = Room.objects.all().order_by('name')
        for room in all_rooms:
            room_labels.append(room.name)
            room_appointment_counts.append(room_counts.get(room.name, 0))

        context['room_labels_json'] = json.dumps(room_labels)
        context['room_appointment_counts_json'] = json.dumps(room_appointment_counts)

        # --- Текущая дата, время и временная зона ---
        context['current_datetime'] = timezone.localtime()
        context['current_timezone_name'] = timezone.get_current_timezone_name()

        logger.info("Загружена страница статистики с расширенными данными.")
        return context


class RandomUserPageView(TemplateView):
    """
    Представление для отображения данных случайного пользователя из RandomUser API.
    """
    template_name = 'random_user_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            response = requests.get('https://randomuser.me/api/')
            response.raise_for_status()
            data = response.json()
            context['user'] = data['results'][0]
            logger.info("Данные случайного пользователя успешно получены.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении данных от RandomUser API: {e}")
            context['user'] = None
            messages.error(self.request, 'Не удалось загрузить данные случайного пользователя. Пожалуйста, попробуйте позже.')
        except (KeyError, IndexError) as e:
            logger.error(f"Некорректный формат данных от RandomUser API: {e}")
            context['user'] = None
            messages.error(self.request, 'Получены некорректные данные от RandomUser API.')
        return context


class OpenLibrarySearchPageView(TemplateView):
    """
    Представление для поиска книг с помощью Open Library API.
    """
    template_name = 'open_library_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        context['search_query'] = search_query
        context['books'] = []

        if search_query:
            api_url = f'http://openlibrary.org/search.json?title={search_query}'
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                context['books'] = data.get('docs', [])[:10]
                logger.info(f"Успешно получены данные от Open Library API для запроса: '{search_query}'.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при запросе к Open Library API для '{search_query}': {e}")
                messages.error(self.request, 'Не удалось получить данные от Open Library API. Пожалуйста, попробуйте позже.')
            except ValueError as e:
                logger.error(f"Ошибка при парсинге JSON от Open Library API: {e}")
                messages.error(self.request, 'Получены некорректные данные от Open Library API.')
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой записи на прием.
    Требует аутентификации.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('core:my_appointments')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Передаем текущего пользователя в форму

        service_id = self.request.GET.get('service_id')
        doctor_id = self.request.GET.get('doctor_id')
        
        if service_id:
            try:
                service = Service.objects.get(pk=service_id)
                kwargs['initial']['service'] = service
            except Service.DoesNotExist:
                messages.error(self.request, 'Выбранная услуга не найдена.')
        
        if doctor_id:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
                kwargs['initial']['doctor'] = doctor
            except Doctor.DoesNotExist:
                messages.error(self.request, 'Выбранный врач не найден.')

        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно создана!')
        logger.info(f"Новая запись создана пользователем {self.request.user.username}.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Записаться на прием"
        logger.info("Загружена форма записи на прием.")
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме записи.')
        logger.warning(f"Ошибка при создании записи: {form.errors}")
        return super().form_invalid(form)


class AppointmentListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка записей на прием текущего пользователя.
    """
    model = Appointment
    template_name = 'my_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        # Фильтруем записи по текущему авторизованному клиенту
        # Проверяем, что у пользователя есть client_profile И что его user_type - 'client'
        if hasattr(self.request.user, 'client_profile') and \
           hasattr(self.request.user, 'user_profile') and \
           self.request.user.user_profile.user_type == 'client':
            queryset = Appointment.objects.filter(client=self.request.user.client_profile).order_by('-date', '-start_time')
            logger.info(f"Загружен список записей для клиента {self.request.user.username}.")
            return queryset
        logger.warning(f"Пользователь {self.request.user.username} не является клиентом или не имеет связанного профиля клиента.")
        return Appointment.objects.none() # Если нет профиля клиента или не клиент, возвращаем пустой queryset


class AppointmentCancelView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Представление для отмены записи на прием.
    Требует аутентификации. Отменить может только клиент, создавший запись,
    и только если запись еще не завершена и не отменена.
    """
    model = Appointment
    template_name = 'appointment_cancel_confirm.html'
    success_url = reverse_lazy('core:my_appointments')
    context_object_name = 'object'

    def test_func(self):
        appointment = self.get_object()
        # Проверяем, что текущий пользователь является клиентом этой записи
        # и что статус записи позволяет ее отменить
        return appointment.client.user == self.request.user and \
               appointment.status == 'planned' and \
               appointment.date >= timezone.localdate() # Можно отменить только будущие записи

    def form_valid(self, form):
        self.object.status = 'cancelled'
        self.object.save()
        messages.success(self.request, 'Запись успешно отменена!')
        logger.info(f"Запись {self.object.id} отменена пользователем {self.request.user.username}.")
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Отменить запись"
        logger.info(f"Загружена страница подтверждения отмены записи {self.get_object().id}.")
        return context

class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление для редактирования существующей записи на прием.
    Требует аутентификации. Редактировать может только клиент, создавший запись.
    Можно редактировать только будущие записи.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('core:my_appointments')
    context_object_name = 'object'

    def test_func(self):
        appointment = self.get_object()
        return appointment.client.user == self.request.user and \
               appointment.date >= timezone.localdate() and \
               appointment.status == 'planned'

    def get_queryset(self):
        return Appointment.objects.filter(client__user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно обновлена!')
        logger.info(f"Запись {self.object.id} обновлена пользователем {self.request.user.username}.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Редактировать запись"
        logger.info(f"Загружена форма редактирования записи {self.object.id}.")
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        logger.warning(f"Ошибка при обновлении записи: {form.errors}")
        return super().form_invalid(form)

class DoctorDetailView(DetailView):
    """
    Представление для детального просмотра информации о враче.
    """
    model = Doctor
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f"Загружена детальная страница врача: {self.object.get_full_name()}.")
        return context


class AllAppointmentsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Представление для отображения всех записей на прием.
    Доступно только суперпользователям.
    """
    model = Appointment
    template_name = 'all_appointments_list.html'
    context_object_name = 'all_appointments'
    paginate_by = 15

    def test_func(self):
        """Проверяет, является ли пользователь суперпользователем."""
        return self.request.user.is_superuser

    def get_queryset(self):
        """Возвращает все записи на прием, отсортированные по дате и времени в обратном порядке."""
        queryset = Appointment.objects.all().order_by('-date', '-start_time')
        logger.info(f"Суперпользователь {self.request.user.username} просматривает все записи на прием.")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Все записи на прием"
        return context


class DoctorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Представление для панели управления врача.
    Отображает расписание врача и записи на прием к нему.
    Доступно только пользователям с user_type 'doctor'.
    """
    template_name = 'doctor_dashboard.html'

    def test_func(self):
        """Проверяет, является ли пользователь врачом."""
        return hasattr(self.request.user, 'user_profile') and self.request.user.user_profile.user_type == 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        doctor = None
        if hasattr(self.request.user, 'user_profile'):
            try:
                # Получаем объект Doctor, связанный с текущим UserProfile
                doctor = self.request.user.user_profile.doctor_profile
            except Doctor.DoesNotExist:
                logger.warning(f"Пользователь {self.request.user.username} с user_type 'doctor' не имеет связанного объекта Doctor.")
                messages.warning(self.request, "Ваш профиль врача не найден. Пожалуйста, свяжитесь с администратором.")
        
        if doctor:
            schedules = Schedule.objects.filter(doctor=doctor).order_by('date', 'start_time')
            context['schedules'] = schedules

            appointments = Appointment.objects.filter(doctor=doctor).select_related('client__user', 'service').order_by('date', 'start_time')
            context['appointments'] = appointments

            context['doctor'] = doctor
            logger.info(f"Загружена панель врача для {doctor.get_full_name()}.")
        else:
            context['schedules'] = []
            context['appointments'] = []
            context['doctor'] = None

        context['title'] = "Панель врача"
        return context


class NewsListView(ListView):
    """
    Представление для отображения списка новостных статей.
    """
    model = NewsArticle
    template_name = 'news_list.html'
    context_object_name = 'news_articles'
    paginate_by = 5

    def get_queryset(self):
        logger.info("Загружен список новостных статей.")
        return NewsArticle.objects.all()


class NewsDetailView(DetailView):
    """
    Представление для отображения одной новостной статьи.
    Использует slug для поиска статьи.
    """
    model = NewsArticle
    template_name = 'news_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f"Загружена детальная страница новости: {self.object.title}.")
        return context

