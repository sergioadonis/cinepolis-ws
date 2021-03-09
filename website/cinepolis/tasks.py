
import logging
from decouple import config
import requests

from website.celery import app
from . import models

logger = logging.getLogger(__name__)


def generate_access_token():
    CINEPOLIS_GRANT_TYPE = config(
        'CINEPOLIS_GRANT_TYPE', default='client_credentials')
    CINEPOLIS_CLIENT_ID = config('CINEPOLIS_CLIENT_ID')
    CINEPOLIS_CLIENT_SECRET = config('CINEPOLIS_CLIENT_SECRET')
    CINEPOLIS_SCOPE = config('CINEPOLIS_SCOPE', default='USER')

    url = 'https://mul-int-oauth2service-production.us-e1.cloudhub.io/api/security/1.0.0/oauth/access-token'
    data = {
        'grant_type': CINEPOLIS_GRANT_TYPE,
        'client_id': CINEPOLIS_CLIENT_ID,
        'client_secret': CINEPOLIS_CLIENT_SECRET,
        'scope': CINEPOLIS_SCOPE
    }

    response = requests.post(url, data=data)
    json = response.json()
    if 'access_token' in json.keys():
        print('SI')
        return json['access_token']
    else:
        print(json)


@app.task
def get_billboard_movies(billboard_request_pk):
    logger.info(f'get_billboard_movies task with {billboard_request_pk} pk')

    billboard_request = models.BillboardRequest.objects.get(
        pk=billboard_request_pk)
    billboard_request.status = models.RequestStatus.DOING
    billboard_request.save()

    try:
        city = billboard_request.city
        city_number, tenant_id = city.city_number, city.tenant_code
        access_token = generate_access_token()

        logger.info(f'access_token {access_token}')

        url = f'https://proxy-mul-exp-browse-production.us-e1.cloudhub.io/v2/exp/browse/cities/{city_number}/billboard?channel=WEB'
        headers = {
            'TenantId': tenant_id,
            'Authorization': 'Bearer ' + access_token
        }

        response = requests.get(url, headers=headers)
        json = response.json()

        billboard_request.response = json
        billboard_request.save()

        for section in json:
            section_name = section['name']
            if section_name == "En Cartelera":
                movies = section['movies']
                billboard_movies = []

                for m in movies:
                    bm = models.BillboardMovie(
                        billboard_request=billboard_request,
                        movie_number=m['id'],
                        movie_title=m['title'],
                        cinemas=m['cinemas']
                    )
                    billboard_movies.append(bm)

                models.BillboardMovie.objects.bulk_create(billboard_movies)
        billboard_request.status = models.RequestStatus.DONE
    except Exception as e:
        billboard_request.status = models.RequestStatus.ERROR
        billboard.error_message = str(e)
        logger.error(e)

    billboard_request.save()
