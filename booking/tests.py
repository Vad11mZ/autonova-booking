from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Booking, Car, Profile


class BookingBusinessRulesTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user('client', password='test12345')
        profile = self.client_user.profile
        profile.role = Profile.Role.CLIENT
        profile.birth_date = date(1995, 1, 1)
        profile.license_years = 5
        profile.save()
        self.car = Car.objects.create(
            brand='Toyota',
            model='Camry',
            category='Бизнес',
            year=2022,
            price_per_day=5000,
            deposit=10000,
        )

    def test_cannot_book_overlapping_dates(self):
        first = Booking.objects.create(
            user=self.client_user,
            car=self.car,
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=6),
            status=Booking.Status.CONFIRMED,
        )
        second = Booking(
            user=self.client_user,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7),
        )
        with self.assertRaises(ValidationError):
            second.full_clean()

    def test_total_price_calculated(self):
        booking = Booking.objects.create(
            user=self.client_user,
            car=self.car,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
        )
        self.assertEqual(booking.total_price, self.car.price_per_day * 2)
