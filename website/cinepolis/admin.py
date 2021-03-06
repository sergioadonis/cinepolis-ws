from django.contrib import admin
from . import models


class CinemaInlineAdmin(admin.TabularInline):
    model = models.Cinema


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city_name', 'city_number']
    inlines = [CinemaInlineAdmin]
