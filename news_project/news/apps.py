from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        from .templatetags.censor import censor
        from django.template import Library
        from django.contrib.auth.models import Group
        common_group, _ = Group.objects.get_or_create(name='common')
        authors_group, _ = Group.objects.get_or_create(name='authors')
        Library().filters['censor'] = censor










