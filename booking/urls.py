from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.UnifiedLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cars/', views.cars, name='cars'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:pk>/cancel/', views.cancel_own_booking, name='cancel_own_booking'),
    path('manager/bookings/', views.manager_bookings, name='manager_bookings'),
    path('fleet/status/', views.fleet_status, name='fleet_status'),
    path('staff/users/', views.staff_users, name='staff_users'),
    path('analytics/', views.analytics, name='analytics'),
]
