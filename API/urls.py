from django.urls import path, include
from rest_framework import routers
from . import views


urlpatterns = [
    path('getpackages', views.GetPackages.as_view(), name='get_packages'),
    path('merge', views.MergeData.as_view(), name='merge'),
]