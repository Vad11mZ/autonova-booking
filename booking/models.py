from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        MANAGER = 'MANAGER', 'Менеджер'
        CLIENT = 'CLIENT', 'Клиент'
        INSPECTOR = 'INSPECTOR', 'Инспектор автопарка'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=30, blank=True, verbose_name='Телефон')
    driver_license = models.CharField(max_length=40, blank=True, verbose_name='Номер ВУ')
    license_years = models.PositiveSmallIntegerField(default=0, verbose_name='Стаж вождения')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.user.username} — {self.get_role_display()}'

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def has_role(self, *roles):
        return self.role in roles


class Car(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Доступен'
        SERVICE = 'SERVICE', 'На обслуживании'
        HIDDEN = 'HIDDEN', 'Скрыт'

    class Transmission(models.TextChoices):
        AT = 'AT', 'Автомат'
        MT = 'MT', 'Механика'
        ROBOT = 'ROBOT', 'Робот'

    brand = models.CharField(max_length=80, verbose_name='Марка')
    model = models.CharField(max_length=80, verbose_name='Модель')
    category = models.CharField(max_length=80, verbose_name='Класс')
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    seats = models.PositiveSmallIntegerField(default=5, verbose_name='Мест')
    transmission = models.CharField(max_length=20, choices=Transmission.choices, default=Transmission.AT)
    fuel_type = models.CharField(max_length=40, default='Бензин', verbose_name='Тип топлива')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за сутки')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Залог')
    city = models.CharField(max_length=80, default='Чита', verbose_name='Город')
    address = models.CharField(max_length=200, default='Центральный офис AutoNova', verbose_name='Адрес выдачи')
    image_url = models.URLField(blank=True, verbose_name='Ссылка на изображение')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    is_active = models.BooleanField(default=True, verbose_name='Показывать на сайте')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['brand', 'model']
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.year})'

    @property
    def title(self):
        return f'{self.brand} {self.model}'

    def active_bookings_qs(self):
        return self.bookings.filter(status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED])

    def future_bookings_qs(self):
        return self.active_bookings_qs().filter(end_date__gte=date.today()).order_by('start_date')

    def has_conflict(self, start_date, end_date, exclude_booking_id=None):
        qs = self.active_bookings_qs().filter(start_date__lt=end_date, end_date__gt=start_date)
        if exclude_booking_id:
            qs = qs.exclude(id=exclude_booking_id)
        return qs.exists()

    def is_booked_now(self):
        today = date.today()
        return self.active_bookings_qs().filter(start_date__lte=today, end_date__gt=today).exists()

    def public_status(self):
        if not self.is_active or self.status == self.Status.HIDDEN:
            return 'Скрыт'
        if self.status == self.Status.SERVICE:
            return 'На обслуживании'
        if self.is_booked_now():
            return 'Авто забронировано'
        if self.future_bookings_qs().exists():
            return 'Есть будущие бронирования'
        return 'Свободен'


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'На рассмотрении'
        CONFIRMED = 'CONFIRMED', 'Подтверждено'
        CANCELLED = 'CANCELLED', 'Отменено'
        COMPLETED = 'COMPLETED', 'Завершено'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='Клиент')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings', verbose_name='Автомобиль')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата возврата')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Итого')
    comment = models.TextField(blank=True, verbose_name='Комментарий клиента')
    manager_comment = models.TextField(blank=True, verbose_name='Комментарий менеджера')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['car', 'start_date', 'end_date']),
            models.Index(fields=['user', 'status']),
        ]
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f'Бронь #{self.pk}: {self.car} — {self.user.username}'

    @property
    def days_count(self):
        if not self.start_date or not self.end_date:
            return 0
        return max((self.end_date - self.start_date).days, 0)

    def calculate_total(self):
        if not self.car_id or not self.start_date or not self.end_date:
            return Decimal('0.00')
        return Decimal(self.days_count) * self.car.price_per_day

    def clean(self):
        errors = {}
        today = date.today()

        if not self.start_date:
            errors['start_date'] = 'Укажите дату начала бронирования.'
        if not self.end_date:
            errors['end_date'] = 'Укажите дату возврата автомобиля.'

        if self.start_date and self.end_date:
            if self.start_date < today:
                errors['start_date'] = 'Нельзя забронировать автомобиль на прошедшую дату.'
            if self.end_date <= self.start_date:
                errors['end_date'] = 'Дата возврата должна быть позже даты начала.'
            if self.days_count > 30:
                errors['end_date'] = 'Максимальный срок бронирования — 30 дней.'

        if self.car_id:
            if not self.car.is_active or self.car.status == Car.Status.HIDDEN:
                errors['car'] = 'Автомобиль временно скрыт и недоступен для бронирования.'
            if self.car.status == Car.Status.SERVICE:
                errors['car'] = 'Автомобиль находится на обслуживании и недоступен для бронирования.'
            if self.start_date and self.end_date and self.car.has_conflict(self.start_date, self.end_date, self.pk):
                errors['car'] = 'Этот автомобиль уже забронирован на выбранные даты. Выберите другой период или другую машину.'

        if self.user_id:
            profile = getattr(self.user, 'profile', None)
            if profile:
                if profile.role != Profile.Role.CLIENT:
                    errors['user'] = 'Бронировать автомобиль может только пользователь с ролью «Клиент».'
                if profile.age is not None and profile.age < 21:
                    errors['user'] = 'Бронирование доступно клиентам старше 21 года.'
                if profile.license_years < 2:
                    errors['user'] = 'Минимальный стаж вождения для бронирования — 2 года.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)
