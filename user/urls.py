from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/check/', views.check_profile, name='check_profile'),
    path('profile/create/step1/', views.profile_create_step1, name='profile_create_step1'),
    path('profile/create/step2/', views.profile_create_step2, name='profile_create_step2'),
    path('profile/create/step3/', views.profile_create_step3, name='profile_create_step3'),
    path('profile/create/step4/', views.profile_create_step4, name='profile_create_step4'),
    path('profile/complete/', views.profile_complete, name='profile_complete'),
    path('weekly_plan/', views.weekly_plan, name='weekly_plan'),
    path('api/get_nutrition/', views.get_nutrition, name='get_nutrition'),  # API 엔드포인트
]