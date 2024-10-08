from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    facility_id = models.CharField(max_length=255)  # 네이버 지도 API에서 제공하는 시설 ID를 저장합니다.
    facility_name = models.CharField(max_length=255)
    facility_address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    detail_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.facility_name}"
