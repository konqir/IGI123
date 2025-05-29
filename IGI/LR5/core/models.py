# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import datetime
import logging
from django.core.exceptions import ValidationError 

from accounts.models import UserProfile 

from .validators import validate_age_18_plus

# Инициализация логгера для приложения core
logger = logging.getLogger(__name__)

class DoctorCategory(models.Model):
    """
    Модель для категорий врачей (например, "Дерматолог", "Косметолог-эстетист").
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория врача"
        verbose_name_plural = "Категории врачей"
        ordering = ['name']

    def __str__(self):
        return self.name

class Doctor(models.Model):
    """
    Модель для врачей косметологического центра.
    Включает ФИО, специализацию, контактные данные, фото и описание.
    """
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    category = models.ForeignKey(DoctorCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="Email")
    description = models.TextField(blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True, verbose_name="Фото")
    # Добавляем связь с UserProfile, чтобы врач был связан с аккаунтом пользователя
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True, verbose_name="Профиль пользователя")


    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ['last_name', 'first_name']

    def get_full_name(self):
        """Возвращает полное имя врача."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    get_full_name.short_description = "Полное имя"

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый врач: {self.get_full_name()}")
        else:
            logger.info(f"Обновлена информация о враче: {self.get_full_name()}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален врач: {self.get_full_name()}")
        super().delete(*args, **kwargs)


class Client(models.Model):
    """
    Модель для хранения дополнительной информации о клиенте,
    связанная с моделью User через OneToOneField.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', primary_key=True)
    phone_number = models.CharField(max_length=20, blank=False, null=False, verbose_name="Номер телефона")
    address = models.CharField(max_length=255, blank=False, null=False, verbose_name="Адрес")
    date_of_birth = models.DateField(
        validators=[validate_age_18_plus],
        blank=False,
        null=False,
        verbose_name="Дата рождения"
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"Клиент: {self.user.username} ({self.user.first_name} {self.user.last_name})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый клиент: {self.user.username}")
        else:
            logger.info(f"Обновлена информация о клиенте: {self.user.username}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален клиент: {self.user.username}")
        super().delete(*args, **kwargs)


class Room(models.Model):
    """
    Модель для косметологических кабинетов.
    """
    name = models.CharField(max_length=100, unique=False, verbose_name="Название кабинета") 
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый кабинет: {self.name}")
        else:
            logger.info(f"Обновлена информация о кабинете: {self.name}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален кабинет: {self.name}")
        super().delete(*args, **kwargs)


class ServiceCategory(models.Model):
    """
    Модель для категорий услуг (например, "Уход за лицом", "Инъекции").
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории услуги")

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлена новая категория услуги: {self.name}")
        else:
            logger.info(f"Обновлена категория услуги: {self.name}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена категория услуги: {self.name}")
        super().delete(*args, **kwargs)


class Service(models.Model):
    """
    Модель для услуг, предлагаемых косметологическим центром.
    """
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Длительность (минут)")
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлена новая услуга: {self.name}")
        else:
            logger.info(f"Обновлена услуга: {self.name}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена услуга: {self.name}")
        super().delete(*args, **kwargs)


class Schedule(models.Model):
    """
    Модель для расписания работы врачей.
    Определяет доступные слоты для записи.
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules', verbose_name="Врач")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кабинет")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        unique_together = ('doctor', 'date', 'start_time') # Врач может иметь только одно расписание на определенное время
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Расписание {self.doctor.get_full_name()} на {self.date} с {self.start_time} до {self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Время начала должно быть раньше времени окончания.')

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        self.full_clean()
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлено новое расписание для врача {self.doctor.get_full_name()} на {self.date}.")
        else:
            logger.info(f"Обновлено расписание для врача {self.doctor.get_full_name()} на {self.date}.")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалено расписание для врача {self.doctor.get_full_name()} на {self.date}.")
        super().delete(*args, **kwargs)


class Appointment(models.Model):
    """
    Модель для записи на прием.
    """
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
        ('no-show', 'Неявка'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments', verbose_name="Клиент")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments', verbose_name="Врач") 
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Услуга")
    date = models.DateField(verbose_name="Дата приема")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая стоимость")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        unique_together = ('doctor', 'date', 'start_time') # Врач не может иметь две записи на одно и то же время
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Запись {self.client.user.username} к {self.doctor.get_full_name()} на {self.date} в {self.start_time}"

    def calculate_total_price(self):
        """Рассчитывает итоговую стоимость записи на основе связанных услуг."""
        price = Decimal('0.00')
        if self.service:
            price += self.service.price
        return price

    def clean(self):
        # Проверка, что дата не в прошлом
        if self.date < timezone.localdate():
            raise ValidationError('Дата приема не может быть в прошлом.')

        # Проверка, что время начала раньше времени окончания
        if self.start_time >= self.end_time:
            raise ValidationError('Время начала приема должно быть раньше времени окончания.')

        # Проверка пересечения с расписанием врача
        schedule_exists = Schedule.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lte=self.start_time,
            end_time__gte=self.end_time
        ).exists()
        if not schedule_exists:
            raise ValidationError('Выбранное время не соответствует расписанию врача.')

        # Проверка на пересечение с другими записями того же врача
        # Исключаем текущую запись при редактировании
        exclude_current = {}
        if self.pk: # Если объект уже имеет первичный ключ, это обновление
            exclude_current = {'pk': self.pk}

        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=['planned', 'completed'] # Учитываем запланированные и завершенные
        ).exclude(**exclude_current)

        if overlapping_appointments.exists():
            raise ValidationError('Выбранное время пересекается с другой записью этого врача.')


    def save(self, *args, **kwargs):
        is_new = self._state.adding
        self.total_price = self.calculate_total_price()
        self.full_clean()
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Создана новая запись: {self}")
        else:
            logger.info(f"Обновлена запись: {self}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена запись: {self}")
        super().delete(*args, **kwargs)


class AppointmentService(models.Model):
    """
    Промежуточная модель для связи записей на прием с услугами.
    Позволяет одной записи иметь несколько услуг.
    """
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='appointment_services', verbose_name="Запись на прием")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Количество")
    price_at_appointment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент записи")

    class Meta:
        verbose_name = "Услуга в записи"
        verbose_name_plural = "Услуги в записи"
        unique_together = ('appointment', 'service') # Одна услуга может быть добавлена только один раз к одной записи

    def __str__(self):
        return f"{self.service.name} для записи {self.appointment.id}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.price_at_appointment:
            self.price_at_appointment = self.service.price # Сохраняем цену услуги на момент добавления
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлена услуга '{self.service.name}' к записи {self.appointment.id}.")
        else:
            logger.info(f"Обновлена услуга '{self.service.name}' в записи {self.appointment.id}.")
        self.appointment.total_price = self.appointment.calculate_total_price()
        self.appointment.save(update_fields=['total_price'])

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена услуга '{self.service.name}' из записи {self.appointment.id}.")
        super().delete(*args, **kwargs)
        self.appointment.total_price = self.appointment.calculate_total_price()
        self.appointment.save(update_fields=['total_price'])


class CompanyInfo(models.Model):
    """
    Модель для хранения общей информации о компании.
    Предполагается, что будет только одна запись.
    """
    text_content = models.TextField(verbose_name="Текстовое содержание о компании")

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return "Информация о компании"

    def save(self, *args, **kwargs):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValidationError('Может существовать только одна запись с информацией о компании.')
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info("Добавлена информация о компании.")
        else:
            logger.info("Обновлена информация о компании.")

    def delete(self, *args, **kwargs):
        logger.info("Удалена информация о компании.")
        super().delete(*args, **kwargs)


class FAQ(models.Model):
    """
    Модель для часто задаваемых вопросов (FAQ).
    """
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    date_added = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Часто задаваемый вопрос (FAQ)"
        verbose_name_plural = "Часто задаваемые вопросы (FAQ)"
        ordering = ['-date_added']

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый FAQ: {self.question}")
        else:
            logger.info(f"Обновлен FAQ: {self.question}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален FAQ: {self.question}")
        super().delete(*args, **kwargs)


class Vacancy(models.Model):
    """
    Модель для вакансий.
    """
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание вакансии")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    published_date = models.DateField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлена новая вакансия: {self.title}")
        else:
            logger.info(f"Обновлена вакансия: {self.title}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена вакансия: {self.title}")
        super().delete(*args, **kwargs)


class Review(models.Model):
    """
    Модель для отзывов клиентов.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews', verbose_name="Клиент")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name="Врач")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name="Услуга")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оценка (от 1 до 5)")
    text = models.TextField(verbose_name="Текст отзыва")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-date_posted']

    def __str__(self):
        return f"Отзыв от {self.client.user.username} ({self.rating} звезд)"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый отзыв от {self.client.user.username}.")
        else:
            logger.info(f"Обновлен отзыв от {self.client.user.username}.")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален отзыв от {self.client.user.username}.")
        super().delete(*args, **kwargs)


class PromoCode(models.Model):
    """
    Модель для промокодов.
    """
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="Процент скидки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания действия")
    date_added = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% скидка)"

    def is_valid(self):
        """Проверяет, активен ли промокод и не истек ли срок его действия."""
        if not self.is_active:
            return False
        if self.expiration_date and self.expiration_date < timezone.localdate():
            return False
        return True

    def save(self, *args, **kwargs):
        """Переопределяем метод save для логирования."""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлен новый промокод: {self.code}")
        else:
            logger.info(f"Обновлен промокод: {self.code}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удален промокод: {self.code}")
        super().delete(*args, **kwargs)


class NewsArticle(models.Model):
    """
    Модель для новостных статей.
    """
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="URL-идентификатор")
    brief_content = models.TextField(verbose_name="Краткое содержание")
    full_content = models.TextField(verbose_name="Полное содержание")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name="Изображение")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Новостная статья"
        verbose_name_plural = "Новостные статьи"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Добавлена новая новостная статья: {self.title}")
        else:
            logger.info(f"Обновлена новостная статья: {self.title}")

    def delete(self, *args, **kwargs):
        logger.info(f"Удалена новостная статья: {self.title}")
        super().delete(*args, **kwargs)

