from django.contrib import admin
from .models import Tag, Thread

admin.site.register(Tag)
admin.site.register(Thread)