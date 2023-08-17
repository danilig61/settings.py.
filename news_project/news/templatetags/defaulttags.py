from django.template.defaulttags import register
from .censor import censor

register.filter('censor', censor)