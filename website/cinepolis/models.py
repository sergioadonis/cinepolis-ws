from django.utils import timezone
from django.db import models
from django.core.validators import validate_comma_separated_integer_list


class City(models.Model):
    city_name = models.CharField(max_length=50)
    city_code = models.CharField(max_length=5, blank=True)
    tenant_code = models.CharField(max_length=5, blank=True)
    billboard_section = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name_plural = 'cities'


class Cinema(models.Model):
    cinema_name = models.CharField(max_length=50)
    cinema_code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.cinema_name


class RequestStatus(models.TextChoices):
    TO_DO = 'TO_DO'
    DOING = 'DOING'
    DONE = 'DONE'
    ERROR = 'ERROR'


class Billboard(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=5, choices=RequestStatus.choices, default=RequestStatus.TO_DO)
    response = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        from django.utils.timezone import template_localtime, localdate
        return f'{localdate(self.date_time)} - {self.city}'


class BillboardMovie(models.Model):
    billboard = models.ForeignKey(
        Billboard, on_delete=models.CASCADE)
    movie_code = models.CharField(max_length=5, blank=True)
    movie_title = models.CharField(max_length=50, blank=True)
    cinemas = models.CharField(max_length=50,
                               validators=[
                                   validate_comma_separated_integer_list],
                               default='',
                               blank=True)
    filter_date_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=5, choices=RequestStatus.choices, default=RequestStatus.TO_DO)
    response = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.movie_title} - {self.billboard}'

    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'


class MovieShowtime(models.Model):
    billboard_movie = models.ForeignKey(
        BillboardMovie, on_delete=models.CASCADE)
    cinema_code = models.CharField(max_length=5, blank=True)
    cinema_name = models.CharField(max_length=50, blank=True)
    session_code = models.CharField(max_length=10, blank=True)
    showtime = models.DateTimeField()
    screen_number = models.CharField(max_length=5, blank=True)
    screen_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.showtime} - {self.screen_name}'
