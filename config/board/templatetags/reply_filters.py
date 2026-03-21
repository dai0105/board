import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def reply_links(text):
    # >>数字 をリンクに変換
    replaced = re.sub(r'>>(\d+)', r'<a href="#reply-\1">>>\1</a>', text)
    return mark_safe(replaced)