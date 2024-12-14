import datetime

from django.forms import (
    ModelForm,
    CharField,
    TextInput,
    PasswordInput,
    ValidationError,
    DateField,
    SelectDateWidget,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordChangeForm
    )


class LoginUserForm(AuthenticationForm):
    """Форма авторизации пользователя"""
    username = CharField(
        label="Логин",
        widget= TextInput(attrs={'class': 'form-input'})
    )
    password = CharField(
        label="Пароль",
        widget= PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    """Форма регистрации пользователя"""
    username = CharField(
        label="Логин",
        widget= TextInput(attrs={'class': 'form-input'})
    )
    password1 = CharField(
        label="Пароль",
        widget=PasswordInput(attrs={'class': 'form-input'})
    )
    password2 = CharField(
        label="Повтор пароля",
        widget= PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': "Имя",
            'last_name': "Фамилия",
        }
        widgets = {
            'email': TextInput(attrs={'class': 'form-input'}),
            'first_name': TextInput(attrs={'class': 'form-input'}),
            'last_name': TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        """Проверка уникальности email адреса"""
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Такой E-mail уже существует!")
        return email


class ProfileUserForm(ModelForm):
    """Форма профиля пользователя"""
    username = CharField(
        disabled=True, # невозможно редактировать
        label='Логин',
        widget= TextInput(attrs={'class': 'form-input'})
    )
    email = CharField(
        disabled=True,
        label='E-mail',
        widget= TextInput(attrs={'class': 'form-input'})
    )
    this_year = datetime.date.today().year
    date_birth = DateField(
        widget= SelectDateWidget(years=tuple(range(this_year-100, this_year-5)))
    )

    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'email', 'date_birth', 'first_name', 'last_name']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-input'}),
            'last_name': TextInput(attrs={'class': 'form-input'}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    """Форма смены пароля"""
    old_password = CharField(
        label="Старый пароль",
        widget= PasswordInput(attrs={'class': 'form-input'})
        )
    new_password1 = CharField(
        label="Новый пароль",
        widget= PasswordInput(attrs={'class': 'form-input'})
        )
    new_password2 = CharField(
        label="Подтверждение пароля",
        widget= PasswordInput(attrs={'class': 'form-input'})
        )
