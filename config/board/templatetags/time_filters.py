from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def jtimesince(value):
    if not value:
        return ""

    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()

    if seconds < 60:
        return "たった今"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes}分前"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours}時間前"
    elif seconds < 86400 * 2:
        return "昨日"
    else:
        days = int(seconds // 86400)
        return f"{days}日前"