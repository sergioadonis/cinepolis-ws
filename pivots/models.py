from django.db import models
from explorer.models import Query


class Pivot(models.Model):
    title = models.CharField(max_length=50, blank=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    options = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        if len(self.title):
            return self.query.title
        return self.title
