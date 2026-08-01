from django.shortcuts import render
from .models import Course
# Create your views here.

def index(request):
    return render(request, 'pages/homepage.html', {'courses':Course.objects.all()})

def files(request):
    return render(request, "pages/filespage.html")

def upload(request):
    return render(request, "pages/upload.html")