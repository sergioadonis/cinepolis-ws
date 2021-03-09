# Generated by Django 3.1 on 2021-03-09 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinepolis', '0008_city_billboard_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cinema',
            name='cinema_number',
        ),
        migrations.RemoveField(
            model_name='city',
            name='city_number',
        ),
        migrations.AddField(
            model_name='cinema',
            name='cinema_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='city',
            name='city_code',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
