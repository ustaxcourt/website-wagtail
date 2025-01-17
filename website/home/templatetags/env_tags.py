from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag(takes_context=True)
def get_enviroment(context):
    return settings.ENVIRONMENT
