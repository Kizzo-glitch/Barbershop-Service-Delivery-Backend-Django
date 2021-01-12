from django import forms
from django.contrib.auth.models import User
from barbershop_app.models import Branches, Service


class ManagerForm(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email")


class ManagerFormEdit(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branches
        fields = ("name", "phone", "address", "logo")


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        exclude = ("branch",)

