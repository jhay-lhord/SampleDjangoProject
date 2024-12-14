
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Employee, Customer
from django.forms import ModelForm

class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username','email')

class employeeForm(ModelForm):
    e_firstname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    e_middlename = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    e_lastname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    e_address = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    e_p_number = forms.CharField(widget=forms.TextInput(attrs={'type': 'tel', 'class' : 'form-control'}))
    e_email = forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'class' : 'form-control'}))
    e_email = forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'class' : 'form-control'}))
    e_password = forms.CharField(widget=forms.TextInput(attrs={'type': 'password', 'class' : 'form-control'}))

    class Meta:
        model = Employee
        fields = ('e_firstname', 'e_middlename', 'e_lastname', 'e_address', 'e_p_number', 'e_email', 'e_password')

class customerForm(ModelForm):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    middlename = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    p_number = forms.CharField(widget=forms.TextInput(attrs={'type': 'tel', 'class' : 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'class' : 'form-control'}))

    class Meta:
        model = Customer
        fields = ('firstname', 'middlename', 'lastname', 'address', 'p_number', 'email')

    def __str__(self):
        return f"{self.firstname} {self.lastname} (ID: {self.customer_id})"
