from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, Transaction, Water_tank, Refill, Sales_Reports
from registration.models import Employee, Customer
from .forms import productForm, transactionForm, waterTankForm, refillForm
from .utils import update_water_tank_after_refill
from django.http import HttpResponseRedirect, FileResponse
import json
from django.views import View
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db import connection
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseRedirect


# imports for generating pdf
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


# Create your views here
def index(request):
    current_datetime = timezone.now()

    five_days_ago = current_datetime - timedelta(days=5)
    date_range = [(current_datetime - timedelta(days=i)).date() for i in range(5, -1, -1)]

    # Initialize an empty list to store total sales for each day
    total_sales_per_day = []

    # Loop through each day in the date range
    for day in date_range:
        sales_data_specific_date = Refill.objects.filter(created_at__date=day).order_by('-created_at')
        for sales in sales_data_specific_date:
            print(sales.total_price)
        sales_specific_data = 0

        for sales in sales_data_specific_date:
            sales_specific_data += sales.total_price
        total_sales_per_day.append(sales_specific_data)
    # convert into json so that it can access with js
    total_sales_per_day_json = json.dumps(total_sales_per_day)
    date_range_labels_json = json.dumps([date.strftime('%Y-%m-%d') for date in date_range])

    # count all the data in the specific models
    customers_count = Customer.objects.all().count()
    products_count = Products.objects.all().count()
    transactions_count = Transaction.objects.all().count()
    total_sales = Sales_Reports.objects.last()

    all_data = {
        'customers': customers_count,
        'products': products_count,
        'transactions': transactions_count,
    }
   
    all_tank_data = Water_tank.objects.all()

    liters_refilled = []
    current_content = []
    for tank in all_tank_data:
        liters_refilled.append(tank.liters_refilled)
        current_content.append(tank.current_content)

    tank_data = {
        'liters_refilled': liters_refilled,
        'current_content': current_content
    }

    tank_data_json = json.dumps(tank_data)

    
    context = {
        'total_sales_per_day_json': total_sales_per_day_json,
        'date_range_labels_json': date_range_labels_json,
        'tank_data_json' : tank_data_json,
        'all_data' : all_data,
        'total_sales': total_sales,
    }
    return render(request, 'index.html', context)
    
def login(request):
    return render(request, 'login.html')

class ProductCreateView(View):
    template_name = 'product.html'
    success_url = '/transaction/product/?submitted=True'
    
    def get(self, request, *args, **kwargs):
        submitted = 'submitted' in request.GET
        
        form = productForm()
        all_product_data = Products.objects.all()
        context = {
            'form': form,
            'submitted': submitted,
            'all_product_data': all_product_data
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle the form submission for POST requests
        form = productForm(request.POST)
        if form.is_valid():
            # Get the form cleaned data
            product_name = form.cleaned_data['name']
            product_description = form.cleaned_data['description']
            product_price = form.cleaned_data['price']
            
            print("Product name:", product_name)
            print("Product description:", product_description)
            print("Product price:", product_price)

            # Call the stored procedure for additional operations (not for inserting data)
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('AddProduct', [product_name, product_description, product_price])
                    print("Stored procedure executed.")
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        all_product_data = Products.objects.all()
        context = {
            'form': form,
            'submitted': False,
            'all_product_data': all_product_data
        }
        return render(request, self.template_name, context)


def update_product(request, pk):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')

        product = Products(
            product_id = pk,
            name = name,
            description = description,
            price = price
        )
        product.save()
        return redirect('product')
    return redirect(request, 'product.html')



def delete_product(request, pk):
    try:
        product = Products.objects.get(product_id=pk) 
        if product:
            product.delete()  
        return redirect('product')  
    except Products.DoesNotExist:
        print("error")
        return redirect('product')


def transaction(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = transactionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/transaction/transaction/?submitted=True")
    else:
        form = transactionForm()
        if 'submitted' in request.GET:
            submitted = True

    # Get all data from the database
    all_transaction_data = Transaction.objects.all()
   
    return render(request, 'transaction.html',  {'form' : form, 'submitted': submitted, 'all_transaction_data' : all_transaction_data})

def update_transaction(request, pk):
    if request.method == "POST":
        customer_id = request.POST.get('customer')
        refill_id = request.POST.get('refill')
        date = request.POST.get('date')
        

        customer = get_object_or_404(Customer, pk=customer_id)
        refill = get_object_or_404(Refill, pk=refill_id)
        print("customer", customer)
        transaction = Transaction(
            transaction_id = pk,
            customer = customer,
            refill = refill,
            date = date
        )
        transaction .save()
        return redirect('transaction')
    return redirect(request, 'transaction.html')


def delete_transaction(request, pk):
    try:
        transaction = Transaction.objects.get(transaction_id=pk)
        if transaction:
            transaction.delete()  
        return redirect('transaction')  
    except Transaction.DoesNotExist:
        return redirect('transaction')

def water_tank(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = waterTankForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/transaction/water_tank/?submitted=True")
    else:
        form = waterTankForm()
        if 'submitted' in request.GET:
            submitted = True
    # Get all data from the database
    all_water_tank_data = Water_tank.objects.all()

   
 
    return render(request,'water_tank.html', {'form' : form, 'submitted': submitted, 'all_water_tank_data' : all_water_tank_data})

def update_water_tank(request, pk):
    if request.method == "POST":
        serial_number = request.POST.get('serial_number')# sad to say na dili ma edit ang serial number kay primary key, you can delete naman
        liters = request.POST.get('liters')

        tank = Water_tank(
            serial_number = pk,
            liters = int(liters), 
        )
        tank.save()
        return redirect('water_tank')
    return redirect(request, 'water_tank.html')

def delete_water_tank(request, pk):
    try:
        water_tank = Water_tank.objects.get(serial_number=pk)
        if water_tank:
            water_tank.delete()  
        return redirect('water_tank')  
    except Transaction.DoesNotExist:
        return redirect('water_tank')
    
class RefillView(View):
    template_name = 'refill.html'
    success_url = '/transaction/refill/?submitted=True'

    def get(self, request, *args, **kwargs):
        submitted = 'submitted' in request.GET

        # Initialize the form and fetch data
        form = refillForm()
        all_refill_data = Refill.objects.all()
        all_product_data = Products.objects.all()
        product_data_json = serialize('json', all_product_data)

        context = {
            'form': form,
            'submitted': submitted,
            'all_refill_data': all_refill_data,
            'product_data_json': product_data_json,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = refillForm(request.POST)
        if form.is_valid():
            # Extract form data
            water_tank = form.cleaned_data['water_tank']
            quantity = form.cleaned_data['quantity']
            total_price = form.cleaned_data['total_price']
            date = form.cleaned_data['date']
            customer = form.cleaned_data['customer']
            product = form.cleaned_data['product']
            created_at = timezone.now()

            
             # Validate and extract water_tank_id
            try:
                water_tank_id = water_tank.serial_number
                customer_id = customer.customer_id
                product_id = product.product_id
            except AttributeError as e:
                return JsonResponse({'error': f'Invalid water tank object: {str(e)}'}, status=400)

            # Call the stored procedure
            try:
                with connection.cursor() as cursor:
                    cursor.callproc(
                        'CheckAndInsertRefill',
                        [date, water_tank_id, quantity, total_price, customer_id, product_id]
                    )
                    
                try:
                    water_tank_instance = Water_tank.objects.get(serial_number=water_tank_id)
                    update_water_tank_after_refill(water_tank_instance, water_tank_instance.pk)
                except Water_tank.DoesNotExist:
                    return JsonResponse({'error': 'Water tank does not exist'}, status=404)
            except Exception as e:
                # Extract the error message, remove single quotes and parentheses
                raw_message = str(e)
                if ":" in raw_message:
                    error_message = raw_message.split(":", 1)[-1].strip()  # Remove error code
                else:
                    error_message = raw_message.strip()

                # Remove any trailing quotes or parentheses
                error_message = error_message.strip("()'")

                return render(
                    self.request,
                    self.template_name,
                    {
                        'error': error_message,
                        'all_refill_data': Refill.objects.all(),
                    },
                )
        

        # If form is invalid, reload the page with errors
        all_refill_data = Refill.objects.all()
        all_product_data = Products.objects.all()
        product_data_json = serialize('json', all_product_data)

        context = {
            'form': form,
            'submitted': False,
            'all_refill_data': all_refill_data,
            'product_data_json': product_data_json,
            'error': 'Form submission failed.',
        }

        return render(request, self.template_name, context)


def update_refill(request, pk):
    if request.method == "POST":
        customer_id = request.POST.get('customer')
        serial_number = request.POST.get('water_tank')
        date = request.POST.get('date')
        quantity = request.POST.get('quantity')
        total_price = request.POST.get('total_price')
        
        customer = get_object_or_404(Customer, pk=customer_id)
        tank = get_object_or_404(Water_tank, pk=serial_number)
        refill = Refill(
            refill_id = pk,
            customer = customer,
            water_tank = tank,
            date = date,
            quantity = quantity,
            total_price = total_price,
            created_at = datetime.now()
            
        )
        refill .save()
        return redirect('refill')
    return redirect(request, 'refill.html')

def delete_refill(request, pk):
    try:
        refill = Refill.objects.get(refill_id=pk)
        if refill:
            refill.delete()  
        return redirect('refill')  
    except Transaction.DoesNotExist:
        return redirect('refill')


def sales(request):
   
    all_sales_data = Sales_Reports.objects.all()

    error_message = None
    isHaveRefillData = []
    
    transaction_id = None
    total_sales = 0
    for sales in all_sales_data:
        # Check if the transaction has a customer
        if sales.transaction_id.customer:

            refills = Refill.objects.filter(customer=sales.transaction_id.customer)

            transaction_id = sales.transaction_id.transaction_id
            firstname = sales.transaction_id.customer.firstname
            lastname = sales.transaction_id.customer.lastname
            total_price = sales.transaction_id.refill.total_price
            total_sales = sales.sales

            refill_data = {
                'firstname' : firstname,
                'lastname' : lastname,
                'transaction_id' : transaction_id,
                'total_price' : total_price,
                'total_sales': total_sales
            }
            isHaveRefillData.append(refill_data)

    
    return render(request, 'sales.html', {'transaction_id' : transaction_id, 'total_sales' : total_sales, 'error_message' : error_message, 'isHaveRefillData' : isHaveRefillData})



def customer_pdf(request):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    all_customer_data = Customer.objects.all()

    # Create table data
    customer_data = [['Customer ID', 'First Name', 'Last Name', 'Phone number', 'Address']]
    for customer in all_customer_data:
        customer_data.append([customer.customer_id, customer.c_firstname, customer.c_lastname,  customer.c_pnumber, customer.c_address])

    # Create a table and set its style
    table = Table(customer_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),  # Other rows background color
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Cell borders
    ]))

    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=30,
    )
    title = "Customer Registration Details"
    elements.append(Paragraph(title, h2_style))
    elements.append(table)


    # Build the PDF document
    doc.build(elements)

    buffer.seek(0)

    # Return the PDF as a response
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    response['Content-Title'] = 'PDF Reports'
    return response


def employee_pdf(request):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    all_employee_data = Employee.objects.all()

    # Create table data
    employee_data = [['Employee ID', 'First Name', 'Last Name', 'Phone number', 'Email', 'Address']]
    for employee in all_employee_data:
        employee_data.append([employee.employee_id, employee.e_firstname, employee.e_lastname,  employee.e_p_number, employee.e_email,  employee.e_address])

    # Create a table and set its style
    table = Table(employee_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgray),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),  # Other rows background color
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cell borders

        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('LEADING', (0, 0), (-1, -1), 14),
    ]))


    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=30,
    )
    title = "Employee Registration Details"
    elements.append(Paragraph(title, h2_style))
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    # Close the buffer and seek to the beginning
    buffer.seek(0)

    # Return the PDF as a response
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    response['Content-Title'] = 'PDF Reports'
    return response

def water_tank_pdf(request):
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    all_water_tank_data = Water_tank.objects.all()

    # Create table data
    water_tank_data = [['Serial Number', 'Total Liters', 'Liters Refilled', 'Current Content']]
    for water_tank in all_water_tank_data:
        water_tank_data.append([water_tank.serial_number, water_tank.liters, water_tank.liters_refilled,  water_tank.current_content])

    # Create a table and set its style
    table = Table(water_tank_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),  # Other rows background color
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Cell borders
    ]))

    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=30,
    )
    title = "Water Tank Details"
    elements.append(Paragraph(title, h2_style))
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    # Close the buffer and seek to the beginning
    buffer.seek(0)

    # Return the PDF as a response
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    response['Content-Title'] = 'PDF Reports'
    return response

def refills_pdf(request):
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    all_refills_data = Refill.objects.all()

    # Create table data
    refill_data = [['Refill ID', 'First Name', ' Last Name', 'Serial Number', 'Date', 'Quantity', 'Total Price']]
    for refill in all_refills_data:
        refill_data.append([refill.refill_id, refill.customer.firstname, refill.customer.lastname,  refill.water_tank.serial_number, refill.date, refill.quantity, refill.total_price])

    # Create a table and set its style
    table = Table(refill_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),  # Other rows background color
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Cell borders
    ]))

    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=30,
    )
    title = "Refill Details"
    elements.append(Paragraph(title, h2_style))
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    # Close the buffer and seek to the beginning
    buffer.seek(0)

    # Return the PDF as a response
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    response['Content-Title'] = 'PDF Reports'
    return response


