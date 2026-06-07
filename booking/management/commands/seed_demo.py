from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from booking.models import Booking, Car, Profile


class Command(BaseCommand):
    help = 'Создает пользователей, автомобили и бронирования для AutoNova Booking.'

    def handle(self, *args, **options):
        users = self.create_users()
        cars = self.create_cars()
        self.create_bookings(users, cars)
        self.stdout.write(self.style.SUCCESS('Данные AutoNova созданы/обновлены.'))
        self.stdout.write('Логины: admin/admin12345, manager/manager12345, inspector/inspector12345, client1/client12345')

    def create_user(self, username, password, role, first_name, last_name, email, phone='', license_years=0, birth_date=None, is_staff=False, is_superuser=False):
        user, created = User.objects.get_or_create(username=username, defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
        })
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.phone = phone
        profile.driver_license = f'75AA{user.id:06d}' if role == Profile.Role.CLIENT else ''
        profile.license_years = license_years
        profile.birth_date = birth_date
        profile.save()
        return user

    def create_users(self):
        return {
            'admin': self.create_user('admin', 'admin12345', Profile.Role.ADMIN, 'Илья', 'Администратор', 'admin@autonova.local', '+7 900 000-00-01', is_staff=True, is_superuser=True),
            'manager': self.create_user('manager', 'manager12345', Profile.Role.MANAGER, 'Мария', 'Менеджер', 'manager@autonova.local', '+7 900 000-00-02', is_staff=True),
            'inspector': self.create_user('inspector', 'inspector12345', Profile.Role.INSPECTOR, 'Павел', 'Инспектор', 'inspector@autonova.local', '+7 900 000-00-03', is_staff=True),
            'client1': self.create_user('client1', 'client12345', Profile.Role.CLIENT, 'Алексей', 'Смирнов', 'client1@mail.local', '+7 914 111-11-11', 5, date(1994, 4, 12)),
            'client2': self.create_user('client2', 'client12345', Profile.Role.CLIENT, 'Екатерина', 'Орлова', 'client2@mail.local', '+7 914 222-22-22', 8, date(1990, 7, 19)),
            'anna': self.create_user('anna', 'client12345', Profile.Role.CLIENT, 'Анна', 'Ким', 'anna@mail.local', '+7 914 333-33-33', 3, date(1998, 9, 4)),
        }

    def create_cars(self):
        demo = [
            ('Toyota', 'Camry', 'Бизнес', 2022, 5, Car.Transmission.AT, 'Бензин', 5200, 15000, 'Комфортный седан бизнес-класса для поездок по городу и командировок.', 'https://upload.wikimedia.org/wikipedia/commons/a/a0/2017_Toyota_Camry_SE%2C_front_right%2C_11-01-2022.jpg'),
            ('Kia', 'Rio', 'Эконом', 2021, 5, Car.Transmission.AT, 'Бензин', 2400, 6000, 'Практичный городской автомобиль с низким расходом топлива.', 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Kia_Rio_sedan_%28Russia%29_%28Front%29.jpg'),
            ('BMW', '320i', 'Премиум', 2020, 5, Car.Transmission.AT, 'Бензин', 6900, 25000, 'Динамичный премиальный седан с отличной управляемостью.', 'https://upload.wikimedia.org/wikipedia/commons/f/f1/2016_BMW_320i_%28F30_LCI_Indonesia%29_looking_from_front.jpg'),
            ('Mercedes-Benz', 'E200', 'Премиум', 2021, 5, Car.Transmission.AT, 'Бензин', 8200, 30000, 'Представительский автомобиль для деловых встреч и комфортных поездок.', 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Mercedes-Benz_E200_AVANTGARDE_Sports_%28W213%29_front.jpg'),
            ('Hyundai', 'Solaris', 'Эконом', 2022, 5, Car.Transmission.AT, 'Бензин', 2600, 6000, 'Надежный автомобиль для ежедневных поездок.', 'https://upload.wikimedia.org/wikipedia/commons/8/8b/2014-2017_Hyundai_Solaris_Sedan_%28front%29.jpg'),
            ('Geely', 'Coolray', 'Кроссовер', 2023, 5, Car.Transmission.ROBOT, 'Бензин', 4300, 12000, 'Современный кроссовер с высоким клиренсом и богатым оснащением.', 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Geely_Coolray_11.jpg'),
            ('Chery', 'Tiggo 7 Pro', 'Кроссовер', 2022, 5, Car.Transmission.ROBOT, 'Бензин', 4700, 13000, 'Просторный кроссовер для семьи и дальних поездок.', 'https://upload.wikimedia.org/wikipedia/commons/2/21/2023_Chery_Tiggo7_Pro_Max_grey_front.jpg'),
            ('Volkswagen', 'Polo', 'Комфорт', 2021, 5, Car.Transmission.AT, 'Бензин', 3100, 8000, 'Сбалансированный седан с удобным салоном.', 'https://upload.wikimedia.org/wikipedia/commons/b/b9/2011_Volkswagen_Polo_Sedan_front.jpg'),
            ('Tesla', 'Model 3', 'Электро', 2021, 5, Car.Transmission.AT, 'Электро', 7600, 28000, 'Электромобиль для тех, кто ценит технологии и тишину.', 'https://upload.wikimedia.org/wikipedia/commons/8/86/Tesla_Model_3_%282023%29_IMG_9488_%28cropped%29.jpg'),
            ('УАЗ', 'Патриот', 'Внедорожник', 2020, 5, Car.Transmission.MT, 'Бензин', 3800, 10000, 'Внедорожник для сложных маршрутов и выездов за город.', 'https://upload.wikimedia.org/wikipedia/commons/0/0d/2018_UAZ_Patriot_silver_front.jpg'),
        ]
        cars = {}
        for brand, model, category, year, seats, transmission, fuel_type, price, deposit, description, image_url in demo:
            car, _ = Car.objects.update_or_create(
                brand=brand,
                model=model,
                year=year,
                defaults={
                    'category': category,
                    'seats': seats,
                    'transmission': transmission,
                    'fuel_type': fuel_type,
                    'price_per_day': Decimal(price),
                    'deposit': Decimal(deposit),
                    'city': 'Чита',
                    'address': 'г. Чита, ул. Бутина, 12, офис AutoNova',
                    'description': description,
                    'image_url': image_url,
                    'status': Car.Status.AVAILABLE,
                    'is_active': True,
                }
            )
            cars[f'{brand} {model}'] = car
        cars['Tesla Model 3'].status = Car.Status.SERVICE
        cars['Tesla Model 3'].save(update_fields=['status'])
        return cars

    def create_bookings(self, users, cars):
        Booking.objects.all().delete()
        today = date.today()
        items = [
            (users['client1'], cars['Toyota Camry'], today + timedelta(days=1), today + timedelta(days=4), Booking.Status.CONFIRMED, 'Нужна подача к офису.'),
            (users['client2'], cars['BMW 320i'], today + timedelta(days=5), today + timedelta(days=8), Booking.Status.PENDING, 'Плановая поездка по городу.'),
            (users['anna'], cars['Geely Coolray'], today + timedelta(days=10), today + timedelta(days=14), Booking.Status.CONFIRMED, 'Нужно детское кресло.'),
            (users['client1'], cars['Kia Rio'], today + timedelta(days=18), today + timedelta(days=20), Booking.Status.PENDING, ''),
        ]
        for user, car, start, end, status, comment in items:
            booking = Booking(user=user, car=car, start_date=start, end_date=end, status=status, comment=comment)
            booking.save()
