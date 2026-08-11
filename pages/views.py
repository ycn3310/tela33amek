from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, JsonResponse
from .models import Course, Paper, Donation

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect


def index(request):
    return render(request, 'pages/homepage.html', {'courses':Course.objects.all()})

def support(request):
    return render(request, 'pages/support.html')

def files(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    papers = Paper.objects.filter(course=course)

    return render(request, "pages/filespage.html", {"course": course,"papers": papers})

def upload(request):
    years = []
    for i in range(2027-1962):
        years.append(f"{2027-i}/{2027-i-1}")
    return render(request, "pages/upload.html", {"courses": Course.objects.all(),"years": years})


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
            "New paper report!!!",
            message,
            settings.EMAIL_HOST_USER,
            ["tela33amek@gmail.com"],
        )

    return redirect("index")


from django.core.mail import EmailMessage

def send_paper(request):
    if request.method == "POST":
        course = request.POST.get("course")
        year = request.POST.get("year")
        uni = request.POST.get("uni")
        teacher = request.POST.get("teacher")
        semester = request.POST.get("semester")
        major = request.POST.get("major")

        paper = request.FILES.get("paper")

        message = f"""
course = {course}, year ={year}
establishment = {uni}, teacher = {teacher}
semester = {semester}, major = {major}
"""

        email = EmailMessage(
            "New paper uploaded!",
            body = message,
            from_email=settings.EMAIL_HOST_USER,
            to=["tela33amek@gmail.com"],
        )

        if paper:
            email.attach(
                paper.name,        
                paper.read(),        
                paper.content_type,  
            )

        email.send()

        return redirect("index")

import boto3
from botocore.config import Config

client = boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )

def view_pdf(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": paper.paper_path.name,
        },
        ExpiresIn=300,
    )

    print(url)

    return redirect(url)

def course_logo(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": course.logo_path.name,
        },
        ExpiresIn=300,
    )

    return redirect(url)

import requests

def make_donation(request):
    if request.method != "POST":
        return redirect("support")

    amount = int(request.POST.get("amount"))
    response = requests.post(
            "https://pay.chargily.net/test/api/v2/checkouts",
            headers={
                "Authorization": f"Bearer {settings.CHARGILY_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            json = {
                "amount": amount,
                "currency": "dzd",
                "success_url": "https://tela33amek.vercel.app/support/success/",
                "failure_url": "https://tela33amek.vercel.app/support/failure/",
                "webhook_endpoint": "https://tela33amek.vercel.app/chargily/webhook/",
                "description": "Support Tela33amek"
            },
        )
    data = response.json()

    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        return redirect("support")

    Donation.objects.create(
        checkout_id = data["id"],
        amount = amount,)

    print(data)
    checkout_url = data["checkout_url"].replace("http://", "https://")
    print(checkout_url)
    return redirect(checkout_url)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Donation
import json

@csrf_exempt
def chargily_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    signature = request.headers.get("signature")

    payload = request.body.decode("utf-8")

    if not signature:
        return HttpResponse(status=400)

    event = json.loads(payload)
    checkout_id = event["data"]["id"]
    event_type = event["type"]

    try: 
        donation = Donation.objects.get(checkout_id = checkout_id)
    except Donation.DoesNotExist:
        return HttpResponse(status = 404)

    if event_type == "checkout.paid":
        donation.status = "paid"
        donation.save()

    elif event_type == "checkout.failed":
            donation.status = "dailed"
            donation.save()

    elif event_type == "checkout.canceled":
            donation.status = "canceled"
            donation.save()

    elif event_type == "checkout.expired":
            donation.status = "expired"
            donation.save()

    return HttpResponse(status=200)