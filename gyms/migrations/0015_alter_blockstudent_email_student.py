# Generated by Django 4.1.5 on 2023-04-05 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0014_alter_blockstudent_email_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockstudent',
            name='email_student',
            field=models.EmailField(max_length=254),
        ),
    ]
