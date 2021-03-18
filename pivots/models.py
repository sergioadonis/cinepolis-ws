from django.db import models
from explorer.models import Query


class Pivot(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    options = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.query.title
