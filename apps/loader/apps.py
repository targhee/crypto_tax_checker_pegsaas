from django.apps import AppConfig


class LoaderConfig(AppConfig):
    name = 'apps.loader'
    label = 'loader'
    default_auto_field = 'django.db.models.BigAutoField'