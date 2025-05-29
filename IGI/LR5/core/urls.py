# core/urls.py
from django.urls import path, re_path
from . import views
from .views import (
    HomeView, CompanyInfoView, FAQListView,
    ContactView, PrivacyPolicyView, VacancyListView, ReviewListView, ReviewCreateView,
    PromoCodeListView, ServiceListView, ServiceDetailView, StatisticsView,
    RandomUserPageView, OpenLibrarySearchPageView,
    AppointmentCreateView, AppointmentListView, AppointmentCancelView, AppointmentUpdateView,
    DoctorDetailView, AllAppointmentsListView, DoctorDashboardView,
    ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    NewsListView, NewsDetailView 
)

app_name = 'core' # Пространство имен для приложения

urlpatterns = [
    path('', HomeView.as_view(), name='home'), # Главная страница
    path('about/', CompanyInfoView.as_view(), name='company_info'), # О компании
    path('faq/', FAQListView.as_view(), name='faq_list'), # FAQ
    path('contacts/', ContactView.as_view(), name='contacts'), # Контакты (врачи)
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'), # Детальная страница врача
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'), # Политика конфиденциальности
    path('vacancies/', VacancyListView.as_view(), name='vacancy_list'), # Вакансии
    path('reviews/', ReviewListView.as_view(), name='review_list'), # Список отзывов
    path('reviews/add/', ReviewCreateView.as_view(), name='add_review'), # Добавление отзыва
    path('promo-codes/', PromoCodeListView.as_view(), name='promo_code_list'), # Промокоды
    path('services/', ServiceListView.as_view(), name='service_list'), # Список услуг
    path('services/add/', ServiceCreateView.as_view(), name='add_service'), # Добавление услуги (только для суперпользователя)
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service_detail'), # Детальный просмотр услуги
    path('services/<int:pk>/edit/', ServiceUpdateView.as_view(), name='edit_service'), # Редактирование услуги (только для суперпользователя)
    path('services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='delete_service'), # Удаление услуги (только для суперпользователя)
    path('statistics/', StatisticsView.as_view(), name='statistics'), # Статистика
    path('appointments/book/', AppointmentCreateView.as_view(), name='book_appointment'), # Форма записи
    path('appointments/my/', AppointmentListView.as_view(), name='my_appointments'), # Мои записи
    path('appointments/<int:pk>/cancel/', AppointmentCancelView.as_view(), name='cancel_appointment'), # Отмена записи
    path('appointments/<int:pk>/edit/', AppointmentUpdateView.as_view(), name='edit_appointment'), # Редактирование записи
    path('appointments/all/', AllAppointmentsListView.as_view(), name='all_appointments_list'), # Все записи (для суперпользователя)
    path('random-user/', RandomUserPageView.as_view(), name='random_user_page'),
    path('search-books/', OpenLibrarySearchPageView.as_view(), name='open_library_search_page'),
    path('news/', NewsListView.as_view(), name='news_list'), # Список новостей
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'), # Детальная страница новости по slug
    path('doctor-dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
]

