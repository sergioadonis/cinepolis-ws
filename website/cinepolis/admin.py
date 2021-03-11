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
    fields = ['movie_title', 'movie_code', 'cinemas']
    show_change_link = True

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.Billboard)
class BillboardAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'city', 'status']
    inlines = [BillboardMovieInline]
    readonly_fields = ['status', 'created_on', 'updated_on']
    exclude = ['error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['date_time', 'city'] + self.readonly_fields
            if obj.status == models.RequestStatus.ERROR:
                readonly_fields = readonly_fields + self.exclude

            if request.user.is_superuser:
                for f in self.list_display:
                    readonly_fields.remove(f)

            return readonly_fields
        return self.readonly_fields


class MovieShowtimeInline(admin.TabularInline):
    model = models.MovieShowtime
    can_delete = False
    fields = ['session_code', 'showtime',
              'cinema_code', 'cinema_name', 'screen_name']

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.BillboardMovie)
class BillboardMovieAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'billboard', 'status']
    inlines = [MovieShowtimeInline]
    readonly_fields = ['status', 'created_on', 'updated_on']
    exclude = ['error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['billboard', 'movie_title',
                               'movie_code', 'cinemas', 'filter_date_time'] + self.readonly_fields
            if obj.status == models.RequestStatus.ERROR:
                readonly_fields = readonly_fields + self.exclude

            if request.user.is_superuser:
                for f in self.list_display:
                    readonly_fields.remove(f)
                readonly_fields.remove('filter_date_time')
                readonly_fields.remove('cinemas')
                readonly_fields.remove('movie_code')

            return readonly_fields
        return self.readonly_fields

    # def has_add_permission(*args, **kwargs):
    #     return False

    # def has_change_permission(*args, **kwargs):
    #     return False
