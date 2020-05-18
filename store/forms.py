from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields=('source',)

class RegisterFrom(UserCreationForm):
    email= forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model=User
        fields=('username','first_name','last_name','email','password1','password2')