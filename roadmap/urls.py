# /exhibit/urls.py

from django.urls import path
from . import views 

app_name = 'roadmap'
urlpatterns = [
    path('', views.map, name='map'),
    path('get-facilities/', views.map, name='get_facilities'),  
]