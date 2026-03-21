from django.db import models
from django.utils import timezone



class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    icon = models.ImageField(upload_to='thread_icons/', blank=True, null=True)  # ← 追加
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def momentum(self):
        # 経過時間（時間）
        hours = max((timezone.now() - self.created_at).total_seconds() / 3600, 1)

        # レス数（Reply モデルの related_name が "replies" の場合）
        reply_count = self.replies.count()

        # 勢い = レス数 ÷ 経過時間
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
    
