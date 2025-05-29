# core/templatetags/core_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Позволяет получить элемент из словаря по ключу в шаблонах Django.
    Использование: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)

