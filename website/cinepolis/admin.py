from django.contrib import admin
from . import models


@admin.register(models.Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ['cinema_name', 'cinema_code']


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city_name', 'city_code', 'tenant_code']


class BillboardMovieInline(admin.TabularInline):
    model = models.BillboardMovie
    can_delete = False

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.BillboardRequest)
class BillboardRequestAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'city', 'status']
    inlines = [BillboardMovieInline]
    readonly_fields = ['status', 'created_on', 'updated_on']
    exclude = ['error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['date_time', 'city'] + self.readonly_fields
            if obj.status == models.RequestStatus.ERROR:
                readonly_fields = readonly_fields + self.exclude
            return readonly_fields
        return self.readonly_fields
