from django.db import models
from django import forms

# Create your models here.


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()


class RegisterForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()
    confirmPassword = forms.CharField()
    firstName = forms.CharField()
    lastName = forms.CharField()
    registerToken = forms.CharField()
