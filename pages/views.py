from django.shortcuts import render, get_object_or_404
from .models import Course, Paper
# Create your views here.

def index(request):
    return render(request, 'pages/homepage.html', {'courses':Course.objects.all()})

def files(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    papers = Paper.objects.filter(course=course)

    return render(request, "pages/filespage.html", {"course": course,"papers": papers})

def upload(request):
    return render(request, "pages/upload.html")