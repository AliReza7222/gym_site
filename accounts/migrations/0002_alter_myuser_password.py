# Generated by Django 4.1.5 on 2023-02-20 17:49

import accounts.validations
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='password',
            field=models.CharField(max_length=100, validators=[accounts.validations.check_password]),
        ),
    ]
