# Generated by Django 4.2 on 2023-12-09 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_alter_employee_e_address_alter_employee_e_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='employee_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
