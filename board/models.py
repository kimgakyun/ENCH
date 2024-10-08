from django.db import models
from django.contrib.auth.models import AbstractUser, User

class Post(models.Model):
    post_title = models.CharField(max_length=255)
    post_content = models.TextField()
    post_timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 문자열 기반 참조
    visitors = models.IntegerField(default=0)

    def __str__(self):
        return self.post_title

class PostImage(models.Model):
    image_url = models.ImageField(upload_to='post_images/', blank=True, null=True)
    image_order = models.IntegerField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
