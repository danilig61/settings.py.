from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

bad_words = ['редиска', 'мат']

@register.filter(name='censor')
def censor(value):
    for word in bad_words:
        value = re.sub(word, '*' * len(word), value, flags=re.IGNORECASE)
    return mark_safe(value)