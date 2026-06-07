from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Booking, Car, Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=80)
    last_name = forms.CharField(label='Фамилия', max_length=80)
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Телефон', max_length=30)
    driver_license = forms.CharField(label='Номер водительского удостоверения', max_length=40)
    license_years = forms.IntegerField(label='Стаж вождения, лет', min_value=0, max_value=70)
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'driver_license', 'license_years', 'birth_date', 'password1', 'password2']
        labels = {'username': 'Логин'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = Profile.Role.CLIENT
            profile.phone = self.cleaned_data['phone']
            profile.driver_license = self.cleaned_data['driver_license']
            profile.license_years = self.cleaned_data['license_years']
            profile.birth_date = self.cleaned_data['birth_date']
            profile.save()
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'comment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Например: нужна детская кресло или подача к офису'}),
        }
        labels = {
            'start_date': 'Дата начала аренды',
            'end_date': 'Дата возврата',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, car=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.car = car
        self.user = user

    def clean(self):
        cleaned = super().clean()
        if not self.car or not self.user:
            raise forms.ValidationError('Не удалось определить автомобиль или пользователя.')
        booking = Booking(
            user=self.user,
            car=self.car,
            start_date=cleaned.get('start_date'),
            end_date=cleaned.get('end_date'),
            comment=cleaned.get('comment', ''),
        )
        try:
            booking.clean()
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages if hasattr(exc, 'messages') else exc)
        return cleaned

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.user = self.user
        booking.car = self.car
        booking.status = Booking.Status.PENDING
        if commit:
            booking.save()
        return booking


class CarStatusForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['status', 'is_active']
        labels = {'status': 'Технический статус', 'is_active': 'Показывать на сайте'}


class ProfileRoleForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role']
        labels = {'role': 'Роль'}
