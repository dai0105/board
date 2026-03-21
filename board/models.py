from django.db import models
from django.utils import timezone
from .utils import upload_to_r2_thread


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    icon = models.ImageField(upload_to=upload_to_r2_thread, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def momentum(self):
        hours = max((timezone.now() - self.created_at).total_seconds() / 3600, 1)
        reply_count = self.replies.count()
        return round(reply_count / hours, 1)

    def __str__(self):
        return self.title

    
class Reply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.TextField(blank=True, null=True)
    video = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.content[:20]
    
