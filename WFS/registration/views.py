from django.shortcuts import render, redirect,  get_object_or_404
from .forms import RegistrationForm, employeeForm, customerForm
from .models import Employee, Customer
from django.views import View
from django.db import connection
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.serializers import serialize


# Create your views here

def user_register(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = employeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')
    else:
        form = employeeForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'register.html', {'form':form, 'submitted' : submitted},)

class UserLoginView(View):
    template = "login.html"

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        email = request.POST['txtEmail']
        pwd = request.POST['Password']
        cursor = connection.cursor()
        args = [email, pwd]
        cursor.callproc('checkCredentials', args)
        result = cursor.fetchall()
        cursor.close()
        if (result[0][0] == 0):
            msg = 'Incorrect username or password'
            return render(request, self.template, {'msg': msg})
        else:
            request.session['username'] = email
            return HttpResponseRedirect('/transaction/index')

class UserLogoutView(View):
    def get(self, request):
        if request.session.get('email'):
            request.session.clear()
        return HttpResponseRedirect(reverse('user_login'))


def employee(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = employeeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/employee/?submmitted=True")
    else:
        form = employeeForm()
        if 'submitted' in request.GET:
            submitted = True
            
    # Get all data from the database and display into the table
    all_employee_data = Employee.objects.all()
    employee_data_json = serialize('json',all_employee_data )
    context = {'form' : form, 
        'submitted': submitted,
        'all_employee_data' : all_employee_data,
        'employee_data_json' : employee_data_json
        }
    
    return render(request, 'employee.html', context)



def update_employee(request, pk):
    if request.method == "POST":
        
        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        lastname = request.POST.get('lastname')
        p_number = request.POST.get('p_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password = request.POST.get('password')

        employee = Employee(
            employee_id = pk,
            e_firstname = firstname,
            e_middlename = middlename,
            e_lastname = lastname,
            e_p_number = p_number,
            e_email = email,
            e_address = address,
            e_password = password
        )
        employee.save()
        return redirect('employee')
        
    return redirect(request, 'employee.html')
   

def delete_employee(request, pk):
    try:
        employee = Employee.objects.get(employee_id=pk)
        if employee:
            employee.delete()  
        return redirect('employee')  
    except Employee.DoesNotExist:
        print("error")
        return redirect('employee') 

def customer(request, pk=None):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = customerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/customer/?submmitted=True")
    else:
        form = customerForm()
        if 'submitted' in request.GET:
            submitted = True


     # Get all data from the database
    all_customer_data = Customer.objects.all()
    context = {
        'form': form, 
        'submitted' : submitted,
        'all_customer_data' : all_customer_data, 
        }
    
    return render(request, 'customer.html',context )

def update_customer(request, pk):
    if request.method == "POST":
        
        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        lastname = request.POST.get('lastname')
        p_number = request.POST.get('p_number')
        email = request.POST.get('email')
        address = request.POST.get('address')

        customer = Customer(
            customer_id = pk,
            firstname = firstname,
            middlename = middlename,
            lastname = lastname,
            p_number = p_number,
            email = email,
            address = address
        )
        customer.save()
        return redirect('customer')
        
    return redirect(request, 'customer.html')
   

def delete_customer(request, pk):
    try:
        customer = Customer.objects.get(customer_id=pk)
        if customer:
            customer.delete()  
        return redirect('customer')  
    except Customer.DoesNotExist:
        print("error")
        return redirect('customer')
