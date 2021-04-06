# Generated by Django 3.1 on 2021-03-18 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pivots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pivot',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pivot',
            name='title',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]