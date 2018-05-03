from django.db import models
from django.forms import ModelForm
from django import forms
from .models import Analyst

#Form to get user login data
class UserForm(forms.Form):
    username = forms.CharField(label="Username", help_text="30 characters or fewer. Letters, digits and @/./+/-/_  only.")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text="Enter the same password as before, for verification.")

#Form to get basic information about a student when they create an account
class AnalystForm(ModelForm):
    class Meta:
        model = Analyst
        fields = ['first_name','last_name','email']
        labels = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        }

