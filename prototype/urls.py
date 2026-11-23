from django.urls import include, path
from .views import home, book;

app_name = 'prototype'
urlpatterns = [
    path('', home, name='home'),
    path("book/", book, name="book"),
]
