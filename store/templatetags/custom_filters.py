from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Memecah string berdasarkan pemisah (key). Contoh: {{ value|split:"," }}"""
    return value.split(key)
