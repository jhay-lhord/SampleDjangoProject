# Generated by Django 4.2 on 2023-12-08 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Container',
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.DeleteModel(
            name='Products',
        ),
        migrations.DeleteModel(
            name='Refill',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
        migrations.AlterField(
            model_name='employee',
            name='employee_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
