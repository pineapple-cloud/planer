from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    AuthenticationForm as DjangoAuthenticationForm
)
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from users.utils import send_email_for_verify

User = get_user_model()

class AuthenticationForm(DjangoAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password,)
            if not self.user_cache.email_verify:
                send_email_for_verify(self.request, self.user_cache)
                raise ValidationError(
                    'Is email verified? Check your email',
                    code='invalid_login',
                )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("username", "email")
class TaskForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['title', 'content', 'day_to_do', 'done', 'tag', 'urgent', 'important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5}),
            'day_to_do': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tag': forms.TextInput(attrs={'class': 'form-control'}),
        }

# class AddTaskForm(forms.Form):
#     title = forms.CharField(label='Название задачи', max_length=255,
#                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название...'}))
#     content = forms.CharField(label='Дополнительная информация',
#         widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Введите подробную информацию о задаче...'}),
#         required=False)
#     day_to_do = forms.DateField(label='Дедлайн', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
#     tag = forms.CharField(label='Тэг', max_length=255,
#                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите тэг задачи'}),
#                           required=False)
#     urgent = forms.BooleanField(label='Срочно', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
#     important = forms.BooleanField(label='Важно', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['title', 'content', 'day_to_do', 'tag', 'urgent', 'important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Введите подробную информацию о задаче...'}),
            'day_to_do': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите тэг задачи'}),
        }