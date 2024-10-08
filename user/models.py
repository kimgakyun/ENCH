from django.contrib.auth.models import AbstractUser, User
from django.db import models
import json

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 개인정보
    name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)  # phone_number에 ImageField가 아닌 CharField 사용

    # 신체 정보 및 병력
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)  # 병력

    # 생활 습관
    dietary_habits = models.TextField(null=True, blank=True)  # 식습관
    activity_level = models.CharField(max_length=50, null=True, blank=True)  # 운동 습관 (주 n회 등)
    sleep_hours = models.FloatField(null=True, blank=True)  # 수면량
    prefer_activity = models.CharField(max_length=20, null=True, blank=True)

    # 목표 설정
    goal_weight = models.FloatField(null=True, blank=True)  # 목표 체중
    goal_strength = models.CharField(max_length=100, null=True, blank=True)  # 근력 목표
    goal_deadline = models.DateField(null=True, blank=True)  # 목표 기한

    def __str__(self):
        return self.user.username
    
class WeeklyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    plan_content = models.JSONField()  # 주간 식단 계획을 JSON으로 저장
    nutrition_info = models.JSONField(null=True) # 식단 계획의 영양 정보를 JSON으로 저장

    def __str__(self):
        return f"{self.user.username} - {self.start_date} ~ {self.end_date}"
    
class MealRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()  # 식사 날짜
    meal_type = models.CharField(max_length=10, choices=[('breakfast', '아침'), ('lunch', '점심'), ('dinner', '저녁')])  # 식사 유형
    actual_food = models.TextField()  # 실제 섭취한 식사 (JSON 또는 텍스트로 저장)
    protein_difference = models.FloatField(blank=True, null=True)  # 단백질 차이
    carb_difference = models.FloatField(blank=True, null=True)  # 탄수화물 차이
    fat_difference = models.FloatField(blank=True, null=True)  # 지방 차이
    
    def __str__(self):
        return f"{self.user.username}'s {self.meal_type} on {self.date}"