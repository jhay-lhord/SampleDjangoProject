from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, Transaction, Water_tank, Refill, Sales_Reports
from registration.models import Employee, Customer
from .forms import productForm, transactionForm, waterTankForm, refillForm
from django.http import HttpResponseRedirect, FileResponse
import json
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.core.serializers import serialize


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
    print(total_sales_per_day)
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

def product(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = productForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/transaction/product/?submitted=True")
    else:
        form = productForm()
        if 'submitted' in request.GET:
            submitted = True

     # Get all data from the database
    all_product_data = Products.objects.all()
    return render(request, 'product.html', {'form' : form, 'submitted': submitted, 'all_product_data' : all_product_data})

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


# mao ni sa delete product prii, sa views.py ni siya ibutang

def delete_product(request, pk):
    try:
        product = Products.objects.get(product_id=pk) #kaning product_id kay mao ni siya ang primary key sa Product na model
        print(product)
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
        print(transaction)
        if transaction:
            transaction.delete()  
        return redirect('transaction')  
    except Transaction.DoesNotExist:
        print("error")
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
        print("refill", water_tank)
        if water_tank:
            water_tank.delete()  
        return redirect('water_tank')  
    except Transaction.DoesNotExist:
        print("error")
        return redirect('water_tank')


def refill(request):
    submitted = False
    if request.method == "POST":
        # Get the form data
        form = refillForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/transaction/refill/?submitted=True")
    else:
        form = refillForm()
        if 'submitted' in request.GET:
            submitted = True
    # Get all data from the database and display into the table
    all_refill_data = Refill.objects.all()
    all_product_data = Products.objects.all() #added
    product_data_json = serialize('json', all_product_data) # added
    print(product_data_json)

    context = {'form' : form,
               'submitted': submitted,
               'all_refill_data' : all_refill_data,
               'product_data_json' : product_data_json  #added
               }
   
    return render(request, 'refill.html', context )

def update_refill(request, pk):
    if request.method == "POST":
        customer_id = request.POST.get('customer')
        serial_number = request.POST.get('water_tank')
        date = request.POST.get('date')
        quantity = request.POST.get('quantity')
        total_price = request.POST.get('total_price')
        
        print("serial_number", serial_number)
        customer = get_object_or_404(Customer, pk=customer_id)
        tank = get_object_or_404(Water_tank, pk=serial_number)
        print("tank", tank)
        print("customer", customer)
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
        print("refill", refill)
        if refill:
            refill.delete()  
        return redirect('refill')  
    except Transaction.DoesNotExist:
        print("error")
        return redirect('refill')


def sales(request):
   
    all_sales_data = Sales_Reports.objects.all()

    error_message = None
    isHaveRefillData = []
    
    transaction_id = None
    total_sales = 0
    for sales in all_sales_data:
        print(sales.transaction_id.transaction_id)
        print("Refill ", sales.transaction_id.refill.total_price)
        # Check if the transaction has a customer
        if sales.transaction_id.customer:

            refills = Refill.objects.filter(customer=sales.transaction_id.customer)

            transaction_id = sales.transaction_id.transaction_id
            firstname = sales.transaction_id.customer.firstname
            lastname = sales.transaction_id.customer.lastname
            total_price = sales.transaction_id.refill.total_price
            total_sales = sales.sales

            refill_data = {
                # 'refills' : refills,
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
        customer_data.append([customer.customer_id, customer.firstname, customer.lastname,  customer.p_number, customer.address])

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


