# Generated manually for AutoNova Booking demo project
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=80, verbose_name='Марка')),
                ('model', models.CharField(max_length=80, verbose_name='Модель')),
                ('category', models.CharField(max_length=80, verbose_name='Класс')),
                ('year', models.PositiveSmallIntegerField(verbose_name='Год')),
                ('seats', models.PositiveSmallIntegerField(default=5, verbose_name='Мест')),
                ('transmission', models.CharField(choices=[('AT', 'Автомат'), ('MT', 'Механика'), ('ROBOT', 'Робот')], default='AT', max_length=20)),
                ('fuel_type', models.CharField(default='Бензин', max_length=40, verbose_name='Тип топлива')),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за сутки')),
                ('deposit', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Залог')),
                ('city', models.CharField(default='Чита', max_length=80, verbose_name='Город')),
                ('address', models.CharField(default='Центральный офис AutoNova', max_length=200, verbose_name='Адрес выдачи')),
                ('image_url', models.URLField(blank=True, verbose_name='Ссылка на изображение')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('AVAILABLE', 'Доступен'), ('SERVICE', 'На обслуживании'), ('HIDDEN', 'Скрыт')], default='AVAILABLE', max_length=20)),
                ('is_active', models.BooleanField(default=True, verbose_name='Показывать на сайте')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Автомобиль',
                'verbose_name_plural': 'Автомобили',
                'ordering': ['brand', 'model'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ADMIN', 'Администратор'), ('MANAGER', 'Менеджер'), ('CLIENT', 'Клиент'), ('INSPECTOR', 'Инспектор автопарка')], default='CLIENT', max_length=20)),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='Телефон')),
                ('driver_license', models.CharField(blank=True, max_length=40, verbose_name='Номер ВУ')),
                ('license_years', models.PositiveSmallIntegerField(default=0, verbose_name='Стаж вождения')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(verbose_name='Дата возврата')),
                ('status', models.CharField(choices=[('PENDING', 'На рассмотрении'), ('CONFIRMED', 'Подтверждено'), ('CANCELLED', 'Отменено'), ('COMPLETED', 'Завершено')], default='PENDING', max_length=20)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Итого')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий клиента')),
                ('manager_comment', models.TextField(blank=True, verbose_name='Комментарий менеджера')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='booking.car', verbose_name='Автомобиль')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Бронирование',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['car', 'start_date', 'end_date'], name='booking_boo_car_id_f10f9c_idx'),
                    models.Index(fields=['user', 'status'], name='booking_boo_user_id_7296cb_idx'),
                ],
            },
        ),
    ]
