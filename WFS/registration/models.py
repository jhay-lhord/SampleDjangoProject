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
    c_firstname = models.CharField(max_length=50, null=False)
    c_middlename = models.CharField(max_length=50, null=True)
    c_lastname = models.CharField(max_length=50, null=False)
    c_address = models.CharField(max_length=100, null=False)
    c_pnumber = models.TextField(max_length=11, null=False)
    c_email = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f"{self.c_firstname} {self.c_lastname} {self.customer_id}"
