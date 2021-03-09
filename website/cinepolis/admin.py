from django.contrib import admin
from . import models


@admin.register(models.Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ['cinema_name', 'cinema_number']


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city_name', 'city_number', 'tenant_code']


class BillboardMovieInline(admin.TabularInline):
    model = models.BillboardMovie
    can_delete = False

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.BillboardRequest)
class BillboardRequestAdmin(admin.ModelAdmin):
    list_display = ['city', 'date', 'status']
    inlines = [BillboardMovieInline]
    readonly_fields = ['status', 'error_message', 'created_on', 'updated_on']
    exclude = ['response']
