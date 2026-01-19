from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter
def is_tomorrow(value):
    """Check if a date is tomorrow"""
    if not value:
        return False
    tomorrow = date.today() + timedelta(days=1)
    return value == tomorrow
