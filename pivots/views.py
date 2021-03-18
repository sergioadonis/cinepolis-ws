from django.http import JsonResponse
from django.db import connection
from decouple import config
from explorer.models import Query

from . import models


def get_pivots(request):
    pivots = models.Pivot.objects.filter(is_active=True)
    data = []
    for p in pivots:
        query = p.query

        with connection.cursor() as cursor:
            cursor.execute(query.sql)
            "Return all rows from a cursor as a dict"
            columns = [col[0] for col in cursor.description]
            query_result = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

            data.append({
                'id': p.id,
                'title': query.title,
                'description': query.description,
                'query_result': query_result,
                'query_id': query.id,
                'options': p.options
            })

    # query_id = config('QUERY_ID', cast=int, default=1)
    # query = Query.objects.get(id=query_id)
    # sql = query.sql

    # with connection.cursor() as cursor:
    #     cursor.execute(sql)
    #     "Return all rows from a cursor as a dict"
    #     columns = [col[0] for col in cursor.description]
    #     query_result = [
    #         dict(zip(columns, row))
    #         for row in cursor.fetchall()
    #     ]

    #     data = {
    #         'query_result': query_result,
    #         'title': query.title
    #     }

    return JsonResponse(data=data, safe=False)
