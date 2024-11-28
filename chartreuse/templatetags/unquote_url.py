from django import template
from urllib.parse import unquote

register = template.Library()

@register.filter(name='unquote_url')
def unquote_url(url: str):
    return unquote(url)
