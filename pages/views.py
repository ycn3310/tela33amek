from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, JsonResponse
from .models import Course, Paper
# Create your views here.

def index(request):
    return render(request, 'pages/homepage.html', {'courses':Course.objects.all()})

def files(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    papers = Paper.objects.filter(course=course)

    return render(request, "pages/filespage.html", {"course": course,"papers": papers})

def upload(request):
    return render(request, "pages/upload.html", {"courses": Course.objects.all()})

def view_pdf(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    return FileResponse(
        paper.paper_path.open("rb"),
        content_type="application/pdf",
        as_attachment=False
    )

def suggestions(request):
    field = request.GET.get("field")
    q = request.GET.get("q", "")

    allowed_fields = ["teacher", "major", "establishment"]

    if field not in allowed_fields:
        return JsonResponse([], safe=False)

    results = (
        Paper.objects.filter(**{f"{field}__icontains": q})
        .values_list(field, flat=True)
        .distinct()[:8]
    )

    return JsonResponse(list(results), safe=False)

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

def report(request, paper_id):
    if request.method == "POST":
        issues = request.POST.getlist("issue")
        description = request.POST.get("description")

        message = f"""
Paper ID: {paper_id}

Issues:
{', '.join(issues)}

Details:
{description}
"""

        send_mail(
            "New paper report",
            message,
            settings.EMAIL_HOST_USER,
            ["tela33amek@gmail.com"],
        )

    return redirect("index")