from django import forms 
from django.forms import TextInput,EmailInput
from django.contrib.auth.models import AbstractBaseUser

class SignUpForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style': 'width: 370px;', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'style':'width:370px;','class':'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'style': 'width: 370px;', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 370px;', 'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 370px;', 'class': 'form-control'}))

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'style':'width:370px;','class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 370px;', 'class': 'form-control'}))

    
# class OtpForm(forms.Form):
#     phone = forms.CharField()
#     otp = forms.CharField()

    # class Meta:
    #         model = AbstractBaseUser
    #         fields = [
    #             'name',  
    #             'email', 
    #             'phone',
    #             'password1', 
    #             'password2', 
    #             ]