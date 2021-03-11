import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from . import tasks

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Billboard)
def billboard_post_save(sender, instance, **kwargs):
    logger.info(f'billboard_post_save signal with {instance.pk} pk')
    if instance.status == models.RequestStatus.TO_DO:
        eta = instance.date_time
        params = (instance.pk,)
        tasks.generate_billboard_movies.apply_async(params, eta=eta)


@receiver(post_save, sender=models.BillboardMovie)
def billboard_movie_post_save(sender, instance, **kwargs):
    logger.info(f'billboard_movie_post_save signal with {instance.pk} pk')
    if instance.status == models.RequestStatus.TO_DO:
        eta = instance.billboard.date_time
        params = (instance.pk,)
        tasks.generate_movie_showtimes.apply_async(params)
