from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import BookingForm, CarStatusForm, ProfileRoleForm, RegistrationForm
from .models import Booking, Car, Profile


class UnifiedLoginView(LoginView):
    template_name = 'booking/login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


def home(request):
    cars = Car.objects.filter(is_active=True).exclude(status=Car.Status.HIDDEN)[:6]
    stats = {
        'cars': Car.objects.filter(is_active=True).exclude(status=Car.Status.HIDDEN).count(),
        'bookings': Booking.objects.exclude(status=Booking.Status.CANCELLED).count(),
        'clients': Profile.objects.filter(role=Profile.Role.CLIENT).count(),
    }
    return render(request, 'booking/home.html', {'cars': cars, 'stats': stats})


def register(request):
    if request.user.is_authenticated:
        return redirect('booking:dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Теперь можно забронировать автомобиль.')
            return redirect('booking:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'booking/register.html', {'form': form})


@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == Profile.Role.CLIENT:
        bookings = request.user.bookings.select_related('car')[:5]
        return render(request, 'booking/dashboard.html', {'profile': profile, 'bookings': bookings})

    stats = get_staff_stats()
    recent_bookings = Booking.objects.select_related('user', 'car')[:8]
    return render(request, 'booking/dashboard.html', {
        'profile': profile,
        'stats': stats,
        'recent_bookings': recent_bookings,
    })


def cars(request):
    queryset = Car.objects.filter(is_active=True).exclude(status=Car.Status.HIDDEN)
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    transmission = request.GET.get('transmission', '').strip()

    if q:
        queryset = queryset.filter(Q(brand__icontains=q) | Q(model__icontains=q) | Q(description__icontains=q))
    if category:
        queryset = queryset.filter(category=category)
    if transmission:
        queryset = queryset.filter(transmission=transmission)

    categories = Car.objects.filter(is_active=True).values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'booking/cars.html', {
        'cars': queryset,
        'categories': categories,
        'q': q,
        'selected_category': category,
        'selected_transmission': transmission,
    })


def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk, is_active=True)
    if car.status == Car.Status.HIDDEN and not request.user.is_staff:
        messages.error(request, 'Автомобиль недоступен.')
        return redirect('booking:cars')

    active_periods = car.future_bookings_qs()
    form = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Для бронирования необходимо войти в аккаунт.')
            return redirect('booking:login')
        if request.user.profile.role != Profile.Role.CLIENT:
            messages.error(request, 'Бронирование доступно только клиентам.')
            return redirect('booking:car_detail', pk=car.pk)

        form = BookingForm(request.POST, car=car, user=request.user)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Заявка #{booking.pk} создана. Автомобиль закреплен за вами на выбранные даты и ожидает подтверждения менеджера.')
            return redirect('booking:my_bookings')
    else:
        if request.user.is_authenticated and request.user.profile.role == Profile.Role.CLIENT:
            form = BookingForm(car=car, user=request.user)

    return render(request, 'booking/car_detail.html', {'car': car, 'form': form, 'active_periods': active_periods})


@login_required
def my_bookings(request):
    bookings = request.user.bookings.select_related('car')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})


@require_POST
@login_required
def cancel_own_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status not in [Booking.Status.PENDING, Booking.Status.CONFIRMED]:
        messages.error(request, 'Это бронирование уже нельзя отменить.')
    elif booking.start_date <= date.today():
        messages.error(request, 'Нельзя отменить бронирование, которое уже началось.')
    else:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Бронирование отменено.')
    return redirect('booking:my_bookings')


@role_required(Profile.Role.ADMIN, Profile.Role.MANAGER)
def manager_bookings(request):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=request.POST.get('booking_id'))
        action = request.POST.get('action')
        if action == 'confirm':
            booking.status = Booking.Status.CONFIRMED
            messages.success(request, f'Бронирование #{booking.pk} подтверждено.')
        elif action == 'cancel':
            booking.status = Booking.Status.CANCELLED
            messages.success(request, f'Бронирование #{booking.pk} отменено.')
        elif action == 'complete':
            booking.status = Booking.Status.COMPLETED
            messages.success(request, f'Бронирование #{booking.pk} завершено.')
        else:
            messages.error(request, 'Неизвестное действие.')
            return redirect('booking:manager_bookings')
        booking.manager_comment = request.POST.get('manager_comment', '').strip()
        booking.save(update_fields=['status', 'manager_comment', 'updated_at', 'total_price'])
        return redirect('booking:manager_bookings')

    status = request.GET.get('status', '')
    bookings = Booking.objects.select_related('user', 'car')
    if status:
        bookings = bookings.filter(status=status)
    return render(request, 'booking/manager_bookings.html', {'bookings': bookings, 'selected_status': status, 'statuses': Booking.Status.choices})


@role_required(Profile.Role.ADMIN, Profile.Role.MANAGER, Profile.Role.INSPECTOR)
def fleet_status(request):
    if request.method == 'POST':
        car = get_object_or_404(Car, pk=request.POST.get('car_id'))
        form = CarStatusForm(request.POST, instance=car)
        if form.is_valid():
            if car.is_booked_now() and form.cleaned_data['status'] == Car.Status.SERVICE:
                messages.error(request, 'Нельзя отправить на обслуживание автомобиль, который сейчас находится в аренде.')
            else:
                form.save()
                messages.success(request, f'Статус автомобиля {car.title} обновлен.')
        else:
            messages.error(request, 'Не удалось обновить статус автомобиля.')
        return redirect('booking:fleet_status')

    cars_list = Car.objects.all().annotate(bookings_count=Count('bookings'))
    return render(request, 'booking/fleet_status.html', {'cars': cars_list, 'status_choices': Car.Status.choices})


@role_required(Profile.Role.ADMIN)
def staff_users(request):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, pk=request.POST.get('profile_id'))
        form = ProfileRoleForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Роль пользователя {profile.user.username} обновлена.')
        else:
            messages.error(request, 'Не удалось обновить роль.')
        return redirect('booking:staff_users')

    profiles = Profile.objects.select_related('user').order_by('role', 'user__username')
    return render(request, 'booking/staff_users.html', {'profiles': profiles, 'roles': Profile.Role.choices})


@role_required(Profile.Role.ADMIN, Profile.Role.MANAGER)
def analytics(request):
    stats = get_staff_stats()
    cars_revenue = Car.objects.annotate(revenue=Sum('bookings__total_price')).order_by('-revenue')[:10]
    return render(request, 'booking/analytics.html', {'stats': stats, 'cars_revenue': cars_revenue})


def get_staff_stats():
    return {
        'cars_total': Car.objects.count(),
        'cars_available': Car.objects.filter(status=Car.Status.AVAILABLE, is_active=True).count(),
        'cars_service': Car.objects.filter(status=Car.Status.SERVICE).count(),
        'bookings_total': Booking.objects.count(),
        'bookings_pending': Booking.objects.filter(status=Booking.Status.PENDING).count(),
        'bookings_confirmed': Booking.objects.filter(status=Booking.Status.CONFIRMED).count(),
        'revenue': Booking.objects.filter(status__in=[Booking.Status.CONFIRMED, Booking.Status.COMPLETED]).aggregate(total=Sum('total_price'))['total'] or 0,
        'clients_total': Profile.objects.filter(role=Profile.Role.CLIENT).count(),
    }
