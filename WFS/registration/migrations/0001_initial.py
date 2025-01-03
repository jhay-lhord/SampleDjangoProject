# Generated by Django 4.2.7 on 2023-11-09 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('container_id', models.IntegerField(max_length=12, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('N', 'New'), ('O', 'Old')], max_length=1)),
                ('size', models.IntegerField(max_length=15)),
                ('price', models.IntegerField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.IntegerField(max_length=10, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=15)),
                ('middlename', models.CharField(max_length=15, null=True)),
                ('lastname', models.CharField(max_length=15)),
                ('address', models.CharField(max_length=30)),
                ('p_number', models.TextField(max_length=11)),
                ('email', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employee_id', models.IntegerField(max_length=11, primary_key=True, serialize=False)),
                ('e_firstname', models.CharField(max_length=15)),
                ('e_middlename', models.CharField(max_length=15, null=True)),
                ('e_lastname', models.CharField(max_length=15)),
                ('e_address', models.CharField(max_length=30)),
                ('e_p_number', models.TextField(max_length=11)),
                ('e_email', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('product_id', models.IntegerField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=30)),
                ('price', models.IntegerField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Refill',
            fields=[
                ('refill_id', models.IntegerField(max_length=12, primary_key=True, serialize=False)),
                ('container_id', models.IntegerField(max_length=15)),
                ('date', models.DateField(max_length=15, null=True)),
                ('quantity', models.IntegerField(max_length=15)),
                ('total_price', models.IntegerField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.IntegerField(max_length=10, primary_key=True, serialize=False)),
                ('customer_id', models.IntegerField(max_length=10)),
                ('date', models.DateField(max_length=11)),
                ('total_amount', models.IntegerField(max_length=11)),
            ],
        ),
    ]
