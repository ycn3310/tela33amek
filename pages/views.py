from django.shortcuts import render
# Create your views here.

def index(request):
    print("new connection")
    return render(request, 'pages/homepage.html')

def files(request):
    print("new connection")
    return render(request, "pages/filespage.html")

def upload(request):
    print("new connection")
    return render(request, "pages/upload.html")