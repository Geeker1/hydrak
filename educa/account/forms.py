from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User




class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254,required=True,widget=forms.EmailInput())
    phone = forms.CharField(max_length=11,required=True,widget=forms.NumberInput())


    class Meta:
        model = User
        fields = ('username', 'email','phone', 'password1', 'password2')