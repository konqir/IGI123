# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Client
from core.validators import validate_age_18_plus
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, ButtonHolder, HTML


class UserUpdateForm(forms.ModelForm):
    """
    Форма для редактирования основной информации пользователя (User).
    """
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('first_name'),
            Field('last_name'),
            Field('email'),
            ButtonHolder(
                Submit('submit', 'Сохранить изменения', css_class='btn-primary')
            )
        )


class ClientUpdateForm(forms.ModelForm):
    """
    Форма для редактирования дополнительной информации клиента (Client).
    """
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_age_18_plus],
        label="Дата рождения",
        help_text="Формат: ДД.ММ.ГГГГ (Возраст должен быть 18 лет или старше)"
    )

    class Meta:
        model = Client
        fields = ['phone_number', 'address', 'date_of_birth']
        labels = {
            'phone_number': 'Номер телефона',
            'address': 'Адрес',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('phone_number'),
            Field('address'),
            Field('date_of_birth'),
            ButtonHolder(
                Submit('submit', 'Сохранить изменения', css_class='btn-primary')
            )
        )


class UserRegistrationForm(UserCreationForm):
    """
    Кастомизированная форма для регистрации нового пользователя,
    включающая поля для User и Client моделей.
    """
    first_name = forms.CharField(max_length=150, required=True, label="Имя")
    last_name = forms.CharField(max_length=150, required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=20, required=True, label="Номер телефона")
    address = forms.CharField(max_length=255, required=True, label="Адрес")
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_age_18_plus],
        required=True,
        label="Дата рождения",
        help_text="Формат: ДД.ММ.ГГГГ (Возраст должен быть 18 лет или старше)"
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('first_name'),
            Field('last_name'),
            Field('email'),
            Field('phone_number'),
            Field('address'),
            Field('date_of_birth'),
            Field('password'),
            Field('password2'),
            ButtonHolder(
                Submit('submit', 'Зарегистрироваться', css_class='btn-primary')
            )
        )

    def save(self, commit=True):
        """
        Сохраняет только объект User.
        Создание объекта Client перемещено в RegisterView.
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

