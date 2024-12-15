from django.db import models
from django.db.models.signals import post_save, post_delete
from registration.models import Customer
from django.dispatch import receiver
from django.db.models import Sum


class Products(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=100, null=False)
    price = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.name}"

class Refill(models.Model):
    refill_id = models.BigAutoField( null=False, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
    product = models.ForeignKey(Products, on_delete = models.CASCADE) #added
    water_tank = models.ForeignKey('Water_Tank', on_delete= models.CASCADE)# i added this foreign key of water tank so that in every refill, the water tank content also updated
    date = models.DateField(max_length=15, null=True)
    quantity = models.IntegerField( null=False)
    total_price = models.IntegerField( null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.c_firstname} {self.customer.c_lastname} {self.refill_id}"

class Water_tank(models.Model):
    serial_number = models.CharField(max_length=100, null=False, primary_key=True)
    liters = models.IntegerField( null=False) 
    liters_refilled = models.IntegerField(null=False)
    current_content = models.IntegerField(null=False)

    def __str__(self):
        return self.serial_number   
    
    @property
    def total_content(self):
        return self.liters

    #calculations for total refill 
    @property
    def total_liters_refilled(self):
        # Calculate the total quantity from related Refill instances
        total_quantity_by_refill_id = Refill.objects.values('refill_id').annotate(total_quantity=Sum('quantity'))

        total_liters = 0
        for entry in total_quantity_by_refill_id:
        # Assuming that 1 gallon of blue water container is 20 liters
            total_liters += entry['total_quantity'] * 20
        return total_liters
    
    @property
    def calculated_current_content(self):
        print("calculated running")
        current = self.total_content - self.total_liters_refilled
        return current


    #save the calculated value into specific fields
    def save(self, *args, **kwargs):
        # Update the 'total_liters_refill' field with the calculated total liters refill
        self.liters_refilled = self.total_liters_refilled
        # Update the 'current_content' field with the calculated current content
        self.current_content = self.calculated_current_content
        super().save(*args, **kwargs)


    @receiver(post_save, sender=Refill)
    @receiver(post_delete, sender=Refill)
    def update_water_tank(sender, instance, **kwargs):
        # Get the associated Water_tank instance
        water_tank = instance.water_tank
        print(water_tank)
        print("update water tank running")

        # Calculate the total quantity for the specific Water_tank
        total_quantity_by_refill_id = Refill.objects.filter(water_tank=water_tank).values('refill_id').annotate(total_quantity=Sum('quantity'))


        total_liters = 0

        # Loop through each entry in the queryset
        for entry in total_quantity_by_refill_id:
            # Assuming that 1 gallon of blue water container is 20 liters
            total_liters += entry['total_quantity'] * 20

        # Update the Water_tank fields
        water_tank.liters_refilled = total_liters
        water_tank.current_content = water_tank.calculated_current_content
        water_tank.save()

        print("Water Tank updated for specific ID")


class Transaction(models.Model):
    transaction_id = models.BigAutoField(null=False, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    refill = models.ForeignKey(Refill, on_delete=models.CASCADE) # i added this refill Foreign key of Transaction so that the customer can refill more than 1, each refill details
    date = models.DateField(max_length=11, null=False)


# The flow of calculating the Sales:
# Add customer details, after that you can now add Refill details, and refill details  needed the customer id
# And in order to calculate the sales, you must choose which customer you want to calculate the sales in the Transaction
# Note: The sales is calculated  after adding Transaction
class Sales_Reports(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='sales_reports_transaction')
    sales = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_sales(self):
        total_sales = Refill.objects.aggregate(models.Sum('total_price'))['total_price__sum']
        print(total_sales)
        return total_sales
    
    # save the calculated total sales
    def save(self, *args, **kwargs):
        self.sales = self.total_sales
        super().save(*args, **kwargs)

# Signal to create a Report instance when a new Transaction instance is created
@receiver(post_save, sender=Transaction)
def create_report_for_transaction(sender, instance, created, **kwargs):
    if created:
        Sales_Reports.objects.create(transaction_id=instance)
        print("instance created")

