from django.db import models
from django.core.validators import validate_comma_separated_integer_list


class City(models.Model):
    city_name = models.CharField(max_length=50)
    city_number = models.PositiveIntegerField()
    tenant_code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name_plural = 'cities'


class Cinema(models.Model):
    cinema_name = models.CharField(max_length=50)
    cinema_number = models.PositiveIntegerField()

    def __str__(self):
        return self.cinema_name


class RequestStatus(models.TextChoices):
    TO_DO = 'TO_DO'
    DOING = 'DOING'
    DONE = 'DONE'
    ERROR = 'ERROR'


class BillboardRequest(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=5, choices=RequestStatus.choices, default=RequestStatus.TO_DO)
    response = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.date} - {self.city}'


class BillboardMovie(models.Model):
    billboard_request = models.ForeignKey(
        BillboardRequest, on_delete=models.CASCADE)
    movie_number = models.PositiveIntegerField()
    movie_title = models.CharField(max_length=50)
    cinemas = models.CharField(max_length=50,
                               validators=[
                                   validate_comma_separated_integer_list],
                               default='')

    def __str__(self):
        return self.movie_title
