# Generated by Django 3.1 on 2021-03-10 05:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinepolis', '0010_auto_20210309_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billboardrequest',
            name='date',
        ),
        migrations.AddField(
            model_name='billboardrequest',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]