# Generated by Django 3.1 on 2021-03-10 05:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cinepolis', '0011_auto_20210309_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billboardrequest',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
