from django.contrib import admin

from .models import Booking, Car, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'license_years', 'birth_date')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'year', 'price_per_day', 'deposit', 'status', 'is_active')
    list_filter = ('status', 'category', 'transmission', 'fuel_type', 'is_active')
    search_fields = ('brand', 'model', 'category', 'city')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'start_date', 'end_date', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'car__brand', 'car__model')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
