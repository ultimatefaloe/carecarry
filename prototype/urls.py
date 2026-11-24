
from django.urls import path
from . import views

app_name = 'prototype'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact, name='contact'),
    path('book-a-move/', views.book_move, name='book_move'),
]
