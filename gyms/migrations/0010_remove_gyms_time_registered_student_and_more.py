# Generated by Django 4.1.5 on 2023-03-26 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0009_timeregisteringym_gyms_time_registered_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gyms',
            name='time_registered_student',
        ),
        migrations.RemoveField(
            model_name='timeregisteringym',
            name='student',
        ),
        migrations.AddField(
            model_name='student',
            name='time_registered_gym',
            field=models.ManyToManyField(blank=True, to='gyms.timeregisteringym'),
        ),
        migrations.AddField(
            model_name='timeregisteringym',
            name='gym_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
