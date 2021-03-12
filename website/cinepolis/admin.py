from django.contrib import admin
from . import models


@admin.register(models.Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ['cinema_name', 'cinema_code']


@admin.register(models.SeatStatus)
class SeatStatusAdmin(admin.ModelAdmin):
    list_display = ['status_name', 'status_code']


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
    list_display = ['date_time', 'city', 'request_status']
    inlines = [BillboardMovieInline]
    readonly_fields = ['request_status', 'created_on', 'updated_on']
    exclude = ['access_token', 'error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['date_time', 'city',
                               'access_token'] + self.readonly_fields
            if obj.request_status == models.RequestStatus.ERROR:
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
    show_change_link = True

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.BillboardMovie)
class BillboardMovieAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'billboard', 'request_status']
    inlines = [MovieShowtimeInline]
    readonly_fields = ['request_status', 'created_on', 'updated_on']
    exclude = ['error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['billboard', 'movie_title',
                               'movie_code', 'cinemas', 'filter_date_time'] + self.readonly_fields
            if obj.request_status == models.RequestStatus.ERROR:
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


class MovieShowtimeSeatStatusInline(admin.TabularInline):
    model = models.MovieShowtimeSeatStatus
    can_delete = False
    fields = ['status_code', 'status_name', 'seat_count']
    show_change_link = True

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False


@admin.register(models.MovieShowtime)
class MovieShowtimeAdmin(admin.ModelAdmin):
    list_display = ['session_code', 'showtime',
                    'billboard_movie', 'request_status']
    inlines = [MovieShowtimeSeatStatusInline]
    readonly_fields = ['request_status', 'created_on', 'updated_on']
    exclude = ['error_message', 'response']

    def get_readonly_fields(self, request, obj=None):
        if not obj is None:
            readonly_fields = ['billboard_movie', 'session_code', 'showtime', 'screen_number',
                               'screen_name', 'cinema_code', 'cinema_name'] + self.readonly_fields
            if obj.request_status == models.RequestStatus.ERROR:
                readonly_fields = readonly_fields + self.exclude

            if request.user.is_superuser:
                for f in self.list_display:
                    readonly_fields.remove(f)
                readonly_fields.remove('screen_number')
                readonly_fields.remove('screen_name')
                readonly_fields.remove('cinema_code')
                readonly_fields.remove('cinema_name')

            return readonly_fields
        return self.readonly_fields

    # def has_add_permission(*args, **kwargs):
    #     return False

    # def has_change_permission(*args, **kwargs):
    #     return False
