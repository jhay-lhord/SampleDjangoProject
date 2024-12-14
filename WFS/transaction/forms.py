from django import forms
from .models import Customer, Products, Transaction, Water_tank, Refill
from django.forms import ModelForm

from datetime import datetime

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
    
class productForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

    class Meta:
        model = Products
        fields = ('name', 'description', 'price')

class transactionForm(ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}),  to_field_name='customer_id')
    refill = forms.ModelChoiceField(queryset=Refill.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}),  to_field_name='refill_id')
    date = forms.CharField(widget=forms.DateInput(attrs={'type': 'date', 'class' : 'form-control'}), initial=datetime.now().strftime('%Y-%m-%d'))

    class Meta:
        model = Transaction
        fields = ('customer', 'refill', 'date')

class waterTankForm(ModelForm):
    serial_number = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    liters = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['liters'].initial = 500000  #assuming that the small tank holds 500000 liters, and 500000 is equal to 500 cubic meter(1l = .001 cubic meter)

    class Meta:
        model = Water_tank
        fields = ('serial_number', 'liters')

class refillForm(ModelForm):#added the product field(line 54)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    product = forms.ModelChoiceField(queryset=Products.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    water_tank = forms.ModelChoiceField(queryset=Water_tank.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    date = forms.CharField(widget=forms.DateInput(attrs={'type': 'date', 'class' : 'form-control'}), initial=datetime.now().strftime('%Y-%m-%d'))
    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control quantity'}))
    total_price = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control total_price'}))

    class Meta:
        model = Refill
        fields = ('customer', 'product', 'water_tank', 'date', 'quantity', 'total_price') #added(product field)

    
