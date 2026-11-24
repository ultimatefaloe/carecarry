
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def how_it_works(request):
    return render(request, 'how-it-works.html')


def contact(request):
    return render(request, 'contact.html')


def book_move(request):
    return render(request, 'book-move.html')
