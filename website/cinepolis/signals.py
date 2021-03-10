import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from . import tasks

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.BillboardRequest)
def billboard_request_post_save(sender, instance, **kwargs):
    logger.info(f'billboard_request_post_save signal with {instance.pk} pk')
    if instance.status == models.RequestStatus.TO_DO:
        eta = instance.date_time
        params = (instance.pk,)
        tasks.get_billboard_movies.apply_async(params, eta=eta)
