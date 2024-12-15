from django.shortcuts import render, redirect,  get_object_or_404
from .forms import RegistrationForm, employeeForm, customerForm
from .models import Employee, Customer
from django.views import View
from django.db import connection
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic.edit import FormView



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


class EmployeeView(FormView):
    template_name = 'employee.html'
    form_class = employeeForm
    success_url = '/employee/?submitted=True'

    def form_valid(self, form):
        # Get cleaned data from the form
        print("running")
        data = form.cleaned_data
        firstname = data.get('e_firstname')
        middlename = data.get('e_middlename', '')  # Optional field
        lastname = data.get('e_lastname')
        address = data.get('e_address')
        phone_number = data.get('e_p_number')
        email = data.get('e_email')
        password = data.get('e_email')
        print(data)

        # Call the stored procedure
        with connection.cursor() as cursor:
            try:
                print("calling procedure")
                cursor.execute(
                    """
                    CALL AddEmployee(%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (firstname, middlename, lastname, address, phone_number, email, password)
                )
                print("done calling procedure")
            except Exception as e:
                # Handle duplicate email or other database errors
                # Extract the error message, remove single quotes and parentheses
                raw_message = str(e)
                if ":" in raw_message:
                    error_message = raw_message.split(":", 1)[-1].strip()  # Remove error code
                else:
                    error_message = raw_message.strip()

                # Remove any trailing quotes or parentheses
                error_message = error_message.strip("()'")
                form = self.form_class()

                return render(
                    self.request,
                    self.template_name,
                    {
                        'form': form,
                        'error': error_message,  # Pass formatted error message
                        'all_employee_data': Employee.objects.all(),
                    },
                )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submitted = self.request.GET.get('submitted', False)
        
        # Fetch all employee data
        all_employee_data = Employee.objects.all()
        employee_data_json = serialize('json', all_employee_data)

        context.update({
            'submitted': submitted,
            'all_employee_data': all_employee_data,
            'employee_data_json': employee_data_json,
        })
        return context

class UpdateEmployeeView(FormView):
    print("running")
    template_name = 'employee.html'  # Your template name
    form_class = employeeForm
    success_url = '/employee/'  # Redirect to the employee list after successful update
    print("running")

    def form_valid(self, form):
        print("running")
        # Get cleaned data from the form
        data = form.cleaned_data
        firstname = data.get('e_firstname')
        middlename = data.get('e_middlename', '')
        lastname = data.get('e_lastname')
        p_number = data.get('e_p_number')
        email = data.get('e_email')
        address = data.get('e_address')
        password = data.get('e_password')

        print(data)

        # Get the employee ID from the URL (passed as pk)
        employee_id = self.kwargs['pk']
        # 
        # Call the stored procedure to update the employee
        with connection.cursor() as cursor:
            try:
                print("calling procedure")
                cursor.execute("""
                    CALL UpdateEmployee(%s, %s, %s, %s, %s, %s, %s, %s)
                """, [employee_id, firstname, middlename, lastname, address, p_number, email, password])
            # 
            except Exception as e:
                # If an error occurs (e.g., duplicate email), catch it and show a message
                # Extract the error message, remove single quotes and parentheses
                raw_message = str(e)
                if ":" in raw_message:
                    error_message = raw_message.split(":", 1)[-1].strip()  # Remove error code
                else:
                    error_message = raw_message.strip()

                # Remove any trailing quotes or parentheses
                error_message = error_message.strip("()'")
                form = self.form_class()
                print(error_message)

                return render(
                    self.request,
                    self.template_name,
                    {
                        'form': form,
                        'error': error_message,  # Pass formatted error message
                        'all_employee_data': Employee.objects.all(),
                    },
                )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 
        # Fetch all employee data
        all_employee_data = Employee.objects.all()
        employee_data_json = serialize('json', all_employee_data)

        context.update({
            'all_employee_data': all_employee_data,
            'employee_data_json': employee_data_json,
        })
        return context
  

def delete_employee(request, pk):
    try:
        employee = Employee.objects.get(employee_id=pk)
        if employee:
            employee.delete()  
        return redirect('employee')  
    except Employee.DoesNotExist:
        print("error")
        return redirect('employee') 


class CustomerView(FormView):
    template_name = 'customer.html'
    form_class = customerForm
    success_url = '/customer/?submitted=True'

    def form_valid(self, form):
        # Get cleaned data from the form
        data = form.cleaned_data
        firstname = data.get('c_firstname')
        middlename = data.get('c_middlename', '')  # Optional field
        lastname = data.get('c_lastname')
        address = data.get('c_address')
        p_number = data.get('c_pnumber')
        email = data.get('c_email')

        # Call the stored procedure to check for duplicate email and insert customer data
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    CALL AddCustomer(%s, %s, %s, %s, %s, %s)
                    """,
                    (firstname, middlename, lastname, address, p_number, email)
                )
            except Exception as e:
                # Handle duplicate email or other database errors
                # Extract the error message, remove single quotes and parentheses
                raw_message = str(e)
                if ":" in raw_message:
                    error_message = raw_message.split(":", 1)[-1].strip()  # Remove error code
                else:
                    error_message = raw_message.strip()

                # Remove any trailing quotes or parentheses
                error_message = error_message.strip("()'")
                form = self.form_class()

                return render(
                    self.request,
                    self.template_name,
                    {
                        'form': form,
                        'error': error_message,  # Pass formatted error message
                        'all_customer_data': Customer.objects.all(),
                    },
                )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submitted = self.request.GET.get('submitted', False)
        
        # Fetch all customer data
        all_customer_data = Customer.objects.all()
        customer_data_json = serialize('json', all_customer_data)

        context.update({
            'submitted': submitted,
            'all_customer_data': all_customer_data,
            'customer_data_json': customer_data_json,
        })
        return context


class UpdateCustomerView(FormView):
    print("running")
    template_name = 'customer.html'  # Your template name
    form_class = customerForm
    success_url = '/customer/'  # Redirect to the employee list after successful update
    print("running")

    def form_valid(self, form):
        print("running")
        # Get cleaned data from the form
        data = form.cleaned_data
        firstname = data.get('c_firstname')
        middlename = data.get('c_middlename', '')
        lastname = data.get('c_lastname')
        p_number = data.get('c_pnumber')
        email = data.get('c_email')
        address = data.get('c_address')

        print(data)

        # Get the employee ID from the URL (passed as pk)
        customer_id = self.kwargs['pk']
        # 
        # Call the stored procedure to update the employee
        with connection.cursor() as cursor:
            try:
                print("calling procedure")
                cursor.execute("""
                    CALL UpdateCustomer(%s, %s, %s, %s, %s, %s, %s)
                """, [customer_id, firstname, middlename, lastname, address, p_number, email])
            # 
            except Exception as e:
                # If an error occurs (e.g., duplicate email), catch it and show a message
                # Extract the error message, remove single quotes and parentheses
                raw_message = str(e)
                if ":" in raw_message:
                    error_message = raw_message.split(":", 1)[-1].strip()  # Remove error code
                else:
                    error_message = raw_message.strip()

                # Remove any trailing quotes or parentheses
                error_message = error_message.strip("()'")
                form = self.form_class()
                print(error_message)

                return render(
                    self.request,
                    self.template_name,
                    {
                        'form': form,
                        'error': error_message,  # Pass formatted error message
                        'all_customer_data': Customer.objects.all(),
                    },
                )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 
        # Fetch all employee data
        all_customer_data = Customer.objects.all()
        customer_data_json = serialize('json', all_customer_data)

        context.update({
            'all_customer_data': all_customer_data,
            'customer_data_json': customer_data_json,
        })
        return context



def delete_customer(request, pk):
    try:
        customer = Customer.objects.get(customer_id=pk)
        if customer:
            customer.delete()  
        return redirect('customer')  
    except Customer.DoesNotExist:
        print("error")
        return redirect('customer')
