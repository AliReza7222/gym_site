# Generated by Django 4.1.5 on 2023-02-26 19:24

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0003_master_profession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='profession',
            field=multiselectfield.db.fields.MultiSelectField(choices=[(1, 'Football'), (2, 'Volleyball'), (3, 'Swim'), (4, 'Basketball'), (5, 'Tennis'), (6, 'Table Tennis'), (7, 'Baseball'), (8, 'Golf'), (9, 'Wrestling'), (10, 'Bodybuilding'), (11, 'Boxing'), (12, 'Kung Fu'), (13, 'Karate'), (14, 'MMA'), (15, 'shooting'), (16, 'Jujitsu'), (17, 'taekwondo'), (18, 'water polo'), (19, 'Running'), (20, 'Mountaineering'), (21, 'Field hockey'), (22, 'bowling'), (23, 'handball'), (24, 'American football'), (25, 'futsal')], max_length=100),
        ),
    ]
