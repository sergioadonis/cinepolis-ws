import logging
import traceback
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
    if response.status_code != 200:
        raise Exception(response.raw)

    json = response.json()
    if 'access_token' in json.keys():
        return json['access_token']
    else:
        logger.debug(json)
        return None


@app.task
def get_billboard_movies(billboard_request_pk):
    logger.info(f'get_billboard_movies task with {billboard_request_pk} pk')

    billboard_request = models.BillboardRequest.objects.get(
        pk=billboard_request_pk)
    billboard_request.status = models.RequestStatus.DOING
    billboard_request.save()

    try:
        city = billboard_request.city
        city_code, tenant_id, billboard_section_name = city.city_code, city.tenant_code, city.billboard_section
        access_token = generate_access_token()

        logger.info(f'access_token {access_token}')

        if access_token is None:
            raise Exception('access_token is None')

        url = f'https://proxy-mul-exp-browse-production.us-e1.cloudhub.io/v2/exp/browse/cities/{city_code}/billboard?channel=WEB'
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
            if section_name == billboard_section_name:
                movies = section['movies']
                billboard_movies = []

                for m in movies:
                    bm = models.BillboardMovie(
                        billboard_request=billboard_request,
                        movie_code=m['id'],
                        movie_title=m['title'],
                        cinemas=m['cinemas']
                    )
                    billboard_movies.append(bm)

                models.BillboardMovie.objects.bulk_create(billboard_movies)
        billboard_request.status = models.RequestStatus.DONE
    except Exception as e:
        billboard_request.status = models.RequestStatus.ERROR
        billboard_request.error_message = str(e)
        logger.error(e)
        traceback.print_exc()

    billboard_request.save()
