# Generated by Django 4.1.5 on 2023-07-04 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='new_notification',
            field=models.CharField(default='0', max_length=1),
        ),
    ]