from django.urls import include, path
from .views import home;

app_name = 'prototype'
urlpatterns = [
    path('', home, name='home'),
]
