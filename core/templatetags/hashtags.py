from django import template
from core.textutils import get_hashtags
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def link_hashtags(value):
    hashtags = get_hashtags(value)
    for tag in hashtags:
        value = value.replace(f"#{tag}", f'<a href="?tag={tag}">#{tag}</a>')
    return mark_safe(value)
