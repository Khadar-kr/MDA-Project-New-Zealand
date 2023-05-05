from django.urls import path
from rest_framework import routers
from django.contrib import admin
from .views import noiseData_list
from .views import noise_detail 

router = routers.SimpleRouter()


urlpatterns = [
    path('noiseData/', noiseData_list),
    path('noiseData/<int:pk>',noise_detail)
]