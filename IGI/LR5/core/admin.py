# core/admin.py
from django.contrib import admin
from .models import (
    DoctorCategory, Doctor, Client, Room, ServiceCategory, Service,
    Schedule, Appointment, AppointmentService, CompanyInfo,
    FAQ, Vacancy, Review, PromoCode, NewsArticle
)

# Регистрация моделей с базовыми настройками
@admin.register(DoctorCategory)
class DoctorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'category', 'phone_number', 'email', 'user_profile')
    list_filter = ('category',)
    search_fields = ('first_name', 'last_name', 'middle_name', 'email', 'phone_number')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'middle_name', 'category', 'photo', 'description', 'user_profile')
        }),
        ('Контактная информация', {
            'fields': ('phone_number', 'email')
        }),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'user_first_name', 'user_last_name', 'phone_number', 'address', 'date_of_birth')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'address')
    list_filter = ('date_of_birth',)
    date_hierarchy = 'date_of_birth'

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Имя пользователя'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'duration_minutes')

class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1
    fields = ('service', 'quantity', 'price_at_appointment')
    readonly_fields = ('price_at_appointment',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'doctor', 'date', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'doctor', 'date')
    search_fields = ('client__user__username', 'doctor__first_name', 'doctor__last_name', 'service__name')
    date_hierarchy = 'date'
    inlines = [AppointmentServiceInline]
    readonly_fields = ('total_price',)

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('text_content',)
    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'date_added')
    search_fields = ('question', 'answer')
    date_hierarchy = 'date_added'

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'published_date')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    date_hierarchy = 'published_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'doctor', 'service', 'rating', 'date_posted')
    list_filter = ('rating', 'doctor', 'service', 'date_posted')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'text')
    date_hierarchy = 'date_posted'

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'expiration_date', 'date_added')
    list_filter = ('is_active', 'expiration_date')
    search_fields = ('code',)
    date_hierarchy = 'date_added'

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'brief_content', 'full_content')
    list_filter = ('published_date',)
    date_hierarchy = 'published_date'
    readonly_fields = ('published_date', 'updated_at',) 
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'image', 'brief_content', 'full_content')
        }),
        ('Даты', {
            'fields': ('published_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'room')
    list_filter = ('doctor', 'date', 'room')
    search_fields = ('doctor__first_name', 'doctor__last_name', 'room__name')
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('doctor', 'date', 'start_time', 'end_time', 'room')
        }),
    )

