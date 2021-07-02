from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.urls import reverse

from . import models


def get_active_pivots(request):
    pivots = models.Pivot.objects.filter(is_active=True).order_by('order')
    return render(request, "index.html", {'pivots': pivots})


def get_pivot_by_id(request, id):
    pivot = models.Pivot.objects.get(id=id)
    return render(request, "get-pivot.html", {'pivot': pivot})


def get_pivot_data_by_id(request, id):
    if (not request.is_ajax()):
        return redirect(to=reverse('get_pivot_by_id', args=[id]))

    p = models.Pivot.objects.get(id=id)
    data = {}
    query = p.query
    if query:
        with connection.cursor() as cursor:
            cursor.execute(query.sql)
            "Return all rows from a cursor as a dict"
            columns = [col[0] for col in cursor.description]
            query_result = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

            data = {
                'id': p.id,
                'title': p.title,
                'description': query.description,
                'query_result': query_result,
                'query_id': query.id,
                'options': p.options
            }

    return JsonResponse(data=data, safe=False)
