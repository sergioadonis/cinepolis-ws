import logging
import traceback
from decouple import config
import requests

from website.celery import app
from . import models

logger = logging.getLogger(__name__)

RETRY_TIMES = config('RETRY_TIMES', default=3, cast=int)


def generate_access_token():
    x_times = 0

    while x_times < RETRY_TIMES:
        x_times += 1
        logger.info(
            f'generate_access_token retry x_times: {x_times}')

        try:
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
                logger.info(f'generate_access_token response: {json}')
        except Exception as e:
            logger.error(f'generate_access_token error: {e}')

    raise Exception(f'Not result after {x_times} retries')


@app.task
def generate_billboard_movies(billboard_pk):
    logger.info(
        f'generate_billboard_movies task with billboard_pk: {billboard_pk}')

    billboard = models.Billboard.objects.get(
        pk=billboard_pk)

    if billboard.request_status != models.RequestStatus.TO_DO:
        return

    billboard.request_status = models.RequestStatus.DOING
    billboard.save()

    x_times = 0

    while x_times < RETRY_TIMES and billboard.request_status != models.RequestStatus.DONE:
        x_times += 1
        logger.info(
            f'generate_billboard_movies retry x_times: {x_times}')

        try:
            access_token = generate_access_token()
            logger.info(f'access_token {access_token}')
            if access_token is None:
                raise Exception('access_token is None')

            billboard.access_token = access_token
            billboard.save()

            city = billboard.city
            cityId, tenantId, billboard_section_name = city.city_code, city.tenant_code, city.billboard_section

            url = f'https://proxy-mul-exp-browse-production.us-e1.cloudhub.io/v2/exp/browse/cities/{cityId}/billboard?channel=WEB'
            logger.info('url: ' + url)

            headers = {
                'TenantId': tenantId,
                'Authorization': 'Bearer ' + access_token
            }

            response = requests.get(url, headers=headers)
            json = response.json()

            billboard.response = json
            billboard.save()

            for section in json:
                section_name = section['name']
                if section_name == billboard_section_name:
                    movies = section['movies']
                    billboard_movies = []

                    for m in movies:
                        cinemas = ','.join(str(cinema)
                                           for cinema in m['cinemas'])

                        exists = models.BillboardMovie.objects.filter(
                            billboard=billboard, movie_code=m['id']).exists()

                        if not exists:
                            bm = models.BillboardMovie(
                                billboard=billboard,
                                movie_code=m['id'],
                                movie_title=m['title'],
                                cinemas=cinemas,
                                filter_date_time=billboard.date_time
                            )
                            billboard_movies.append(bm)
                            bm.save()

                    # models.BillboardMovie.objects.bulk_create(billboard_movies)

            billboard.request_status = models.RequestStatus.DONE
            billboard.save()
        except Exception as e:
            billboard.request_status = models.RequestStatus.ERROR
            billboard.error_message = str(e)
            logger.error(e)
            traceback.print_exc()
            billboard.save()

    return True


@app.task
def generate_movie_showtimes(billboard_movie_pk):
    logger.info(
        f'generate_movie_showtimes task with billboard_movie_pk: {billboard_movie_pk}')

    billboard_movie = models.BillboardMovie.objects.get(
        pk=billboard_movie_pk)

    if billboard_movie.request_status != models.RequestStatus.TO_DO:
        return

    billboard_movie.request_status = models.RequestStatus.DOING
    billboard_movie.save()

    x_times = 0

    while x_times < RETRY_TIMES and billboard_movie.request_status != models.RequestStatus.DONE:
        x_times += 1
        logger.info(
            f'generate_movie_showtimes retry x_times: {x_times}')

        try:
            access_token = billboard_movie.billboard.access_token
            logger.info(f'access_token {access_token}')
            if access_token is None:
                raise Exception('access_token is None')

            dt = billboard_movie.filter_date_time
            # import json
            # from django.core.serializers.json import DjangoJSONEncoder
            # filter_date = json.dumps(date_time, cls=DjangoJSONEncoder)
            # filter_date = f'{dt.year}-{dt.month}-{dt.day}T{dt.hour}:{dt.minute}:{dt.second}'
            from django.utils import timezone
            filterDate = dt.astimezone(
                timezone.get_current_timezone()).strftime("%Y-%m-%dT%H:%M:%S")
            movieId, cinemaId = billboard_movie.movie_code, billboard_movie.cinemas

            url = f'https://proxy-mul-exp-browse-production.us-e1.cloudhub.io/v1/exp/browse/cinemas/showtimes?channel=WEB&movieId={movieId}&cinemaId={cinemaId}&filterDate={filterDate}'
            logger.info('url: ' + url)

            tenantId = billboard_movie.billboard.city.tenant_code

            headers = {
                'TenantId': tenantId,
                'Authorization': 'Bearer ' + access_token
            }

            response = requests.get(url, headers=headers)
            json = response.json()

            billboard_movie.response = json
            billboard_movie.save()

            cinemas = list(models.Cinema.objects.all().values(
                'cinema_name', 'cinema_code'))

            for c in json:
                for m in c['movies']:
                    for v in m['versions']:
                        version_details = ' '.join(
                            (v['experience'], v['language'], v['format'],))
                        movie_showtimes = []
                        for s in v['showtimes']:
                            import datetime
                            showtime = datetime.datetime.strptime(
                                s['showtime'], "%Y-%m-%dT%H:%M:%S")
                            showtime = timezone.make_aware(
                                showtime, timezone=timezone.get_current_timezone())

                            cinema_code = c['cinemaId']
                            cinema_name = ''
                            logger.info(cinemas)
                            filtered_cinemas = list(filter(
                                lambda x: x['cinema_code'] == str(cinema_code), cinemas))
                            logger.info(filtered_cinemas)
                            if len(filtered_cinemas) > 0:
                                cinema_name = filtered_cinemas[0]['cinema_name']

                            exists = models.MovieShowtime.objects.filter(
                                billboard_movie=billboard_movie, session_code=s['sessionId']).exists()

                            if not exists:
                                ms = models.MovieShowtime(
                                    billboard_movie=billboard_movie,
                                    cinema_code=cinema_code,
                                    cinema_name=cinema_name,
                                    session_code=s['sessionId'],
                                    showtime=showtime,
                                    screen_number=s['screenNumber'],
                                    screen_name=s['screenName'],
                                    version_details=version_details
                                )
                                movie_showtimes.append(ms)
                                ms.save()

                        # models.MovieShowtime.objects.bulk_create(movie_showtimes)

            billboard_movie.request_status = models.RequestStatus.DONE
            billboard_movie.save()
        except Exception as e:
            billboard_movie.request_status = models.RequestStatus.ERROR
            billboard_movie.error_message = str(e)
            billboard_movie.save()
            logger.error(e)
            traceback.print_exc()

    return True


@app.task
def generate_movie_showtime_seats(movie_showtime_pk):
    logger.info(
        f'generate_movie_showtime_seats task with movie_showtime_pk: {movie_showtime_pk}')

    movie_showtime = models.MovieShowtime.objects.get(
        pk=movie_showtime_pk)

    if movie_showtime.request_status != models.RequestStatus.TO_DO:
        return

    movie_showtime.request_status = models.RequestStatus.DOING
    movie_showtime.save()

    x_times = 0

    while x_times < RETRY_TIMES and movie_showtime.request_status != models.RequestStatus.DONE:
        x_times += 1
        logger.info(
            f'generate_billboard_movies retry x_times: {x_times}')

        try:
            access_token = movie_showtime.billboard_movie.billboard.access_token
            logger.info(f'access_token {access_token}')
            if access_token is None:
                raise Exception('access_token is None')

            cinemaId, sessionId = movie_showtime.cinema_code, movie_showtime.session_code

            url = f'https://proxy-mul-exp-browse-production.us-e1.cloudhub.io/v2/exp/browse/cinemas/{cinemaId}/sessions/{sessionId}/seats?channel=WEB'
            logger.info('url: ' + url)

            tenantId = movie_showtime.billboard_movie.billboard.city.tenant_code

            headers = {
                'TenantId': tenantId,
                'Authorization': 'Bearer ' + access_token
            }

            response = requests.get(url, headers=headers)
            json = response.json()

            movie_showtime.response = json
            movie_showtime.save()

            showtime_seat_status = {}

            for a in json['seatLayoutData']['areas']:
                for r in a['rows']:
                    for s in r['seats']:
                        status_code = str(s['status'])

                        showtime_seat_status[status_code] = showtime_seat_status.get(
                            status_code, 0) + 1

                        # showtime_seats.append({
                        #     'status_code': status_code,
                        #     'status_name': status_name
                        # })

            seat_status = list(models.SeatStatus.objects.all().values(
                'status_name', 'status_code'))

            movie_showtime_seat_status = []

            for (status_code, seat_count) in showtime_seat_status.items():
                status_name = ''
                filtered_status = list(
                    filter(lambda x: x['status_code'] == status_code, seat_status))
                if len(filtered_status) > 0:
                    status_name = filtered_status[0]['status_name']

                exists = models.MovieShowtimeSeatStatus.objects.filter(
                    movie_showtime=movie_showtime, status_code=status_code).exists()

                if not exists:
                    msss = models.MovieShowtimeSeatStatus(movie_showtime=movie_showtime,
                                                          status_code=status_code, status_name=status_name, seat_count=seat_count)
                    movie_showtime_seat_status.append(msss)
                    msss.save()

            # models.MovieShowtimeSeatStatus.objects.bulk_create(movie_showtime_seat_status)
            movie_showtime.request_status = models.RequestStatus.DONE
            movie_showtime.save()
        except Exception as e:
            movie_showtime.request_status = models.RequestStatus.ERROR
            movie_showtime.error_message = str(e)
            movie_showtime.save()
            logger.error(e)
            traceback.print_exc()

    return True
