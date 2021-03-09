from django.apps import AppConfig


class CinepolisConfig(AppConfig):
    name = 'cinepolis'

    def ready(self):
        try:
            from . import signals
        except ModuleNotFoundError as err:
            print(err)
