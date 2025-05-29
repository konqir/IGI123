# core/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Review, Doctor, Service, Appointment, Schedule, ServiceCategory, Client
from django.forms import ValidationError
from django.utils import timezone
import datetime

# Импортируем Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, ButtonHolder, HTML

# from .validators import validate_age_18_plus 

class ReviewForm(forms.ModelForm):
    """
    Форма для добавления нового отзыва клиентом.
    """
    class Meta:
        model = Review
        fields = ['doctor', 'service', 'rating', 'text']
        labels = {
            'doctor': 'Врач (необязательно)',
            'service': 'Услуга (необязательно)',
            'rating': 'Ваша оценка',
            'text': 'Текст отзыва',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('doctor'),
            Field('service'),
            Field('rating'),
            Field('text'),
            ButtonHolder(
                Submit('submit', 'Оставить отзыв', css_class='btn-primary')
            )
        )

class AppointmentForm(forms.ModelForm):
    """
    Форма для записи на прием или редактирования существующей записи.
    """
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Дата приема"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Время начала"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Время окончания"
    )

    class Meta:
        model = Appointment
        fields = ['client', 'doctor', 'service', 'date', 'start_time', 'end_time', 'notes']
        labels = {
            'client': 'Клиент',
            'doctor': 'Врач',
            'service': 'Услуга (необязательно)',
            'date': 'Дата приема',
            'start_time': 'Время начала',
            'end_time': 'Время окончания',
            'notes': 'Примечания',
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('client'),
            Field('doctor'),
            Field('service'),
            Field('date'),
            Field('start_time'),
            Field('end_time'),
            Field('notes'),
            ButtonHolder(
                Submit('submit', 'Записаться на прием', css_class='btn-primary')
            )
        )

        if self.user and not self.user.is_superuser:
            # Скрываем поле 'client' для обычных пользователей
            self.fields['client'].widget = forms.HiddenInput()
            if hasattr(self.user, 'client_profile'):
                self.fields['client'].initial = self.user.client_profile
            # Для обычных пользователей кнопка будет "Записаться на прием"
            self.helper.layout[-1][0].value = 'Записаться на прием'
        else:
            # Для суперпользователей кнопка будет "Сохранить изменения"
            if self.instance.pk:
                self.helper.layout[-1][0].field_classes = 'btn-success'
                self.helper.layout[-1][0].value = 'Сохранить изменения'
            else:
                self.helper.layout[-1][0].value = 'Создать запись'

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        service = cleaned_data.get('service')
        client = cleaned_data.get('client')

        # Проверка, что клиент установлен для обычных пользователей (если поле скрыто)
        if self.user and not self.user.is_superuser:
            if not client or not hasattr(self.user, 'client_profile') or client != self.user.client_profile:
                self.add_error('client', "Вы не можете создать запись для другого клиента. Выберите свой профиль.")
                # Дополнительная проверка на случай, если client_profile не существует
                if not hasattr(self.user, 'client_profile'):
                    self.add_error(None, "Ваш профиль клиента не найден. Пожалуйста, свяжитесь с администратором.")

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "Время окончания должно быть позже времени начала.")
        
        if service and start_time and end_time:
            service_duration = service.duration_minutes
            dummy_date = datetime.date(2000, 1, 1) 
            start_dt = datetime.datetime.combine(dummy_date, start_time)
            end_dt = datetime.datetime.combine(dummy_date, end_time)
            slot_duration_minutes = (end_dt - start_dt).total_seconds() / 60

            if slot_duration_minutes < service_duration:
                self.add_error('service', f"Выбранный временной слот ({int(slot_duration_minutes)} мин.) слишком короткий для выбранной услуги ({service_duration} мин.).")
            
        if self.instance and self.instance.pk and self.instance.status != 'planned' and self.user and not self.user.is_superuser:
             self.add_error(None, "Нельзя редактировать завершенные или отмененные записи.")

        if doctor and date and start_time and end_time:
            schedule_exists = Schedule.objects.filter(
                doctor=doctor,
                date=date,
                start_time__lte=start_time,
                end_time__gte=end_time
            ).exists()
            if not schedule_exists:
                self.add_error(None, "Выбранное время не соответствует расписанию врача или слот слишком длинный для его расписания.")
            
            # Проверка на пересечение с другими записями того же врача
            overlapping_appointments = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            # Исключаем текущую запись при редактировании
            if self.instance and self.instance.pk:
                overlapping_appointments = overlapping_appointments.exclude(pk=self.instance.pk)

            if overlapping_appointments.exists():
                self.add_error(None, "Выбранное время пересекается с уже существующей записью. Пожалуйста, выберите другой временной слот.")
        
        return cleaned_data

class ServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг.
    """
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration_minutes', 'category']
        labels = {
            'name': 'Название услуги',
            'description': 'Описание услуги',
            'price': 'Цена',
            'duration_minutes': 'Длительность (минут)',
            'category': 'Категория',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name'),
            Field('description'),
            Field('price'),
            Field('duration_minutes'),
            Field('category'),
            ButtonHolder(
                Submit('submit', 'Сохранить услугу', css_class='btn-primary')
            )
        )
        if self.instance.pk:
            self.helper.layout[-1][0].value = 'Обновить услугу'
            self.helper.layout[-1][0].field_classes = 'btn-success'

