from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.security import HttpBearer

from .models import Booking, Car, Profile


# ── Auth ──────────────────────────────────────────────────────────────────


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.select_related('profile').get(id=payload['user_id'])
        except Exception:
            return None


def make_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=getattr(settings, 'JWT_EXPIRY_DAYS', 7))
    return jwt.encode({'user_id': user.id, 'exp': exp}, settings.SECRET_KEY, algorithm='HS256')


def require_role(user: User, *roles):
    profile = getattr(user, 'profile', None)
    if not profile or profile.role not in roles:
        raise HttpError(403, 'Недостаточно прав.')


bearer = AuthBearer()
api = NinjaAPI(title='AutoNova Booking API', version='2.0.0')


# ── Schemas ───────────────────────────────────────────────────────────────


class LoginIn(Schema):
    username: str
    password: str


class RegisterIn(Schema):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str = ''
    phone: str = ''
    birth_date: Optional[date] = None
    license_years: int = 0
    driver_license: str = ''


class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    phone: str


class TokenOut(Schema):
    token: str
    user: UserOut


class CarOut(Schema):
    id: int
    brand: str
    model: str
    category: str
    year: int
    seats: int
    transmission: str
    fuel_type: str
    price_per_day: Decimal
    deposit: Decimal
    city: str
    address: str
    image_url: str
    description: str
    status: str
    public_status: str


class AvailabilityOut(Schema):
    car_id: int
    available: bool
    message: str


class BookingIn(Schema):
    car_id: int
    start_date: date
    end_date: date
    comment: str = ''


class BookingOut(Schema):
    id: int
    car_id: int
    car: str
    client: str
    start_date: date
    end_date: date
    status: str
    status_display: str
    total_price: Decimal
    comment: str
    manager_comment: str
    created_at: str


class ManagerActionIn(Schema):
    action: str
    manager_comment: str = ''


class CarStatusIn(Schema):
    status: str


class ProfileRoleIn(Schema):
    role: str


class ProfileOut(Schema):
    id: int
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    role_display: str
    phone: str


class StatsOut(Schema):
    cars: int
    bookings: int
    clients: int


class CarRevenueOut(Schema):
    car: str
    revenue: str


class AnalyticsOut(Schema):
    cars_total: int
    cars_available: int
    cars_service: int
    bookings_total: int
    bookings_pending: int
    bookings_confirmed: int
    revenue: Decimal
    clients_total: int
    cars_revenue: List[CarRevenueOut]


class FleetCarOut(Schema):
    id: int
    brand: str
    model: str
    year: int
    category: str
    status: str
    status_display: str
    is_booked_now: bool
    bookings_count: int
    price_per_day: Decimal


# ── Helpers ───────────────────────────────────────────────────────────────


def _user_out(user: User) -> UserOut:
    p = getattr(user, 'profile', None)
    return UserOut(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=p.role if p else '',
        phone=p.phone if p else '',
    )


def _car_out(car: Car) -> CarOut:
    return CarOut(
        id=car.id,
        brand=car.brand,
        model=car.model,
        category=car.category,
        year=car.year,
        seats=car.seats,
        transmission=car.get_transmission_display(),
        fuel_type=car.fuel_type,
        price_per_day=car.price_per_day,
        deposit=car.deposit,
        city=car.city,
        address=car.address,
        image_url=car.image_url,
        description=car.description,
        status=car.status,
        public_status=car.public_status(),
    )


def _booking_out(b: Booking) -> BookingOut:
    return BookingOut(
        id=b.id,
        car_id=b.car_id,
        car=b.car.title,
        client=f'{b.user.get_full_name()} ({b.user.username})',
        start_date=b.start_date,
        end_date=b.end_date,
        status=b.status,
        status_display=b.get_status_display(),
        total_price=b.total_price,
        comment=b.comment,
        manager_comment=b.manager_comment,
        created_at=b.created_at.isoformat(),
    )


# ── Auth endpoints ────────────────────────────────────────────────────────


@api.post('/auth/login', response=TokenOut, tags=['auth'])
def login(request, payload: LoginIn):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        raise HttpError(401, 'Неверный логин или пароль.')
    return TokenOut(token=make_token(user), user=_user_out(user))


@api.post('/auth/register', response=TokenOut, tags=['auth'])
def register(request, payload: RegisterIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, 'Пользователь с таким логином уже существует.')
    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
    )
    profile = user.profile
    profile.phone = payload.phone
    profile.birth_date = payload.birth_date
    profile.license_years = payload.license_years
    profile.driver_license = payload.driver_license
    profile.save()
    return TokenOut(token=make_token(user), user=_user_out(user))


@api.get('/auth/me', response=UserOut, auth=bearer, tags=['auth'])
def me(request):
    return _user_out(request.auth)


# ── Public ────────────────────────────────────────────────────────────────


@api.get('/stats', response=StatsOut, tags=['public'])
def stats(request):
    return StatsOut(
        cars=Car.objects.filter(is_active=True).exclude(status=Car.Status.HIDDEN).count(),
        bookings=Booking.objects.exclude(status=Booking.Status.CANCELLED).count(),
        clients=Profile.objects.filter(role=Profile.Role.CLIENT).count(),
    )


# ── Cars ──────────────────────────────────────────────────────────────────


@api.get('/cars', response=List[CarOut], tags=['cars'])
def cars_list(request, q: str = '', category: str = '', transmission: str = ''):
    qs = Car.objects.filter(is_active=True).exclude(status=Car.Status.HIDDEN)
    if q:
        qs = qs.filter(Q(brand__icontains=q) | Q(model__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    if transmission:
        qs = qs.filter(transmission=transmission)
    return [_car_out(c) for c in qs]


@api.get('/cars/categories', response=List[str], tags=['cars'])
def cars_categories(request):
    return list(
        Car.objects.filter(is_active=True)
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )


@api.get('/cars/{car_id}', response=CarOut, tags=['cars'])
def car_get(request, car_id: int):
    return _car_out(get_object_or_404(Car, id=car_id, is_active=True))


@api.get('/cars/{car_id}/availability', response=AvailabilityOut, tags=['cars'])
def car_availability(request, car_id: int, start_date: date, end_date: date):
    car = get_object_or_404(Car, id=car_id, is_active=True)
    if car.status != Car.Status.AVAILABLE:
        return AvailabilityOut(car_id=car.id, available=False, message=f'Автомобиль недоступен: {car.get_status_display()}')
    if start_date < date.today() or end_date <= start_date:
        return AvailabilityOut(car_id=car.id, available=False, message='Проверьте даты бронирования.')
    if car.has_conflict(start_date, end_date):
        return AvailabilityOut(car_id=car.id, available=False, message='Авто забронировано на выбранные даты.')
    return AvailabilityOut(car_id=car.id, available=True, message='Автомобиль свободен на выбранные даты.')


# ── Client bookings ───────────────────────────────────────────────────────


@api.post('/bookings', response=BookingOut, auth=bearer, tags=['bookings'])
def booking_create(request, payload: BookingIn):
    profile = getattr(request.auth, 'profile', None)
    if not profile or profile.role != Profile.Role.CLIENT:
        raise HttpError(403, 'Создание бронирований доступно только клиенту.')
    car = get_object_or_404(Car, id=payload.car_id, is_active=True)
    booking = Booking(
        user=request.auth, car=car,
        start_date=payload.start_date, end_date=payload.end_date,
        comment=payload.comment or '',
    )
    try:
        booking.full_clean()
    except ValidationError as exc:
        msgs = []
        if hasattr(exc, 'message_dict'):
            for field_msgs in exc.message_dict.values():
                msgs.extend(field_msgs)
        else:
            msgs = exc.messages
        raise HttpError(400, ' '.join(msgs))
    booking.save()
    return _booking_out(booking)


@api.get('/bookings/my', response=List[BookingOut], auth=bearer, tags=['bookings'])
def my_bookings(request):
    return [_booking_out(b) for b in request.auth.bookings.select_related('car', 'user')]


@api.post('/bookings/{booking_id}/cancel', auth=bearer, tags=['bookings'])
def cancel_booking(request, booking_id: int):
    booking = get_object_or_404(Booking, id=booking_id, user=request.auth)
    if booking.status not in [Booking.Status.PENDING, Booking.Status.CONFIRMED]:
        raise HttpError(400, 'Это бронирование уже нельзя отменить.')
    if booking.start_date <= date.today():
        raise HttpError(400, 'Нельзя отменить бронирование, которое уже началось.')
    booking.status = Booking.Status.CANCELLED
    booking.save()
    return {'ok': True}


# ── Manager ───────────────────────────────────────────────────────────────


@api.get('/manager/bookings', response=List[BookingOut], auth=bearer, tags=['manager'])
def manager_bookings(request, status: str = ''):
    require_role(request.auth, Profile.Role.ADMIN, Profile.Role.MANAGER)
    qs = Booking.objects.select_related('user', 'car')
    if status:
        qs = qs.filter(status=status)
    return [_booking_out(b) for b in qs]


@api.post('/manager/bookings/{booking_id}/action', auth=bearer, tags=['manager'])
def manager_booking_action(request, booking_id: int, payload: ManagerActionIn):
    require_role(request.auth, Profile.Role.ADMIN, Profile.Role.MANAGER)
    booking = get_object_or_404(Booking, id=booking_id)
    action_map = {
        'confirm': Booking.Status.CONFIRMED,
        'cancel': Booking.Status.CANCELLED,
        'complete': Booking.Status.COMPLETED,
    }
    if payload.action not in action_map:
        raise HttpError(400, 'Неизвестное действие.')
    booking.status = action_map[payload.action]
    booking.manager_comment = payload.manager_comment
    booking.save()
    return {'ok': True}


# ── Fleet ─────────────────────────────────────────────────────────────────


@api.get('/fleet', response=List[FleetCarOut], auth=bearer, tags=['fleet'])
def fleet_list(request):
    require_role(request.auth, Profile.Role.ADMIN, Profile.Role.MANAGER, Profile.Role.INSPECTOR)
    cars = Car.objects.annotate(bookings_count=Count('bookings'))
    return [
        FleetCarOut(
            id=c.id, brand=c.brand, model=c.model, year=c.year,
            category=c.category, status=c.status,
            status_display=c.get_status_display(),
            is_booked_now=c.is_booked_now(),
            bookings_count=c.bookings_count,
            price_per_day=c.price_per_day,
        )
        for c in cars
    ]


@api.patch('/fleet/{car_id}/status', auth=bearer, tags=['fleet'])
def fleet_update_status(request, car_id: int, payload: CarStatusIn):
    require_role(request.auth, Profile.Role.ADMIN, Profile.Role.MANAGER, Profile.Role.INSPECTOR)
    if payload.status not in Car.Status.values:
        raise HttpError(400, 'Неверный статус.')
    car = get_object_or_404(Car, id=car_id)
    if car.is_booked_now() and payload.status == Car.Status.SERVICE:
        raise HttpError(400, 'Нельзя отправить на обслуживание автомобиль, который сейчас в аренде.')
    car.status = payload.status
    car.save()
    return {'ok': True}


# ── Admin / Users ─────────────────────────────────────────────────────────


@api.get('/admin/users', response=List[ProfileOut], auth=bearer, tags=['admin'])
def admin_users(request):
    require_role(request.auth, Profile.Role.ADMIN)
    profiles = Profile.objects.select_related('user').order_by('role', 'user__username')
    return [
        ProfileOut(
            id=p.id, user_id=p.user.id,
            username=p.user.username,
            first_name=p.user.first_name, last_name=p.user.last_name,
            email=p.user.email, role=p.role,
            role_display=p.get_role_display(), phone=p.phone,
        )
        for p in profiles
    ]


@api.patch('/admin/users/{profile_id}/role', auth=bearer, tags=['admin'])
def admin_update_role(request, profile_id: int, payload: ProfileRoleIn):
    require_role(request.auth, Profile.Role.ADMIN)
    if payload.role not in Profile.Role.values:
        raise HttpError(400, 'Неверная роль.')
    profile = get_object_or_404(Profile, id=profile_id)
    profile.role = payload.role
    profile.save()
    return {'ok': True}


# ── Analytics ─────────────────────────────────────────────────────────────


@api.get('/analytics', response=AnalyticsOut, auth=bearer, tags=['analytics'])
def analytics(request):
    require_role(request.auth, Profile.Role.ADMIN, Profile.Role.MANAGER)
    raw = (
        Car.objects.annotate(revenue=Sum('bookings__total_price'))
        .order_by('-revenue')[:10]
        .values('brand', 'model', 'revenue')
    )
    return AnalyticsOut(
        cars_total=Car.objects.count(),
        cars_available=Car.objects.filter(status=Car.Status.AVAILABLE, is_active=True).count(),
        cars_service=Car.objects.filter(status=Car.Status.SERVICE).count(),
        bookings_total=Booking.objects.count(),
        bookings_pending=Booking.objects.filter(status=Booking.Status.PENDING).count(),
        bookings_confirmed=Booking.objects.filter(status=Booking.Status.CONFIRMED).count(),
        revenue=Booking.objects.filter(
            status__in=[Booking.Status.CONFIRMED, Booking.Status.COMPLETED]
        ).aggregate(t=Sum('total_price'))['t'] or Decimal('0'),
        clients_total=Profile.objects.filter(role=Profile.Role.CLIENT).count(),
        cars_revenue=[
            CarRevenueOut(car=f"{r['brand']} {r['model']}", revenue=str(r['revenue'] or 0))
            for r in raw
        ],
    )
