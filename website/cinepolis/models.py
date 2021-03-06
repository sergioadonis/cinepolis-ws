from django.db import models


class City(models.Model):
    city_name = models.CharField(max_length=50)
    city_number = models.PositiveIntegerField()

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name_plural = 'cities'


class Cinema(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    cinema_name = models.CharField(max_length=50)
    cinema_number = models.PositiveIntegerField()

    def __str__(self):
        return self.cinema_name
