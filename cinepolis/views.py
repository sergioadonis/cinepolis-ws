from django.http import JsonResponse
from django.db import connection
from decouple import config
from explorer.models import Query

from . import models


def data_view(request):
    query_id = config('QUERY_ID', cast=int, default=1)
    query = Query.objects.get(id=query_id)
    sql = query.sql

    with connection.cursor() as cursor:
        cursor.execute(sql)
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        data = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return JsonResponse(data=data, safe=False)
