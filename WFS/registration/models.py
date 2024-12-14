from django.db import models


class Employee(models.Model):
    employee_id = models.BigAutoField(null=False, primary_key=True)
    e_firstname = models.CharField(max_length=100, null=False)
    e_middlename = models.CharField(max_length=100, null=True)
    e_lastname = models.CharField(max_length=100, null=False)
    e_address = models.CharField(max_length=100, null=False)
    e_p_number = models.TextField(max_length=20, null=False)
    e_email = models.CharField(max_length=50, null=False)
    e_password = models.CharField(max_length = 50, null=False)


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=50, null=False)
    middlename = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=100, null=False)
    p_number = models.TextField(max_length=11, null=False)
    email = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.customer_id}"
