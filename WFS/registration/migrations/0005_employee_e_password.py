# Generated by Django 4.2 on 2023-12-12 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_alter_employee_employee_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='e_password',
            field=models.CharField(default='password123', max_length=50),
            preserve_default=False,
        ),
    ]