from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, JsonResponse, Http404
from django.db.models import Prefetch
from .models import Course, Paper, Chapter, Donation, User, Plan, Subscription

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

from django.core.mail import EmailMessage


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Donation
import json

import time

def get_current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return User.objects.filter(id=user_id, is_active=True).first()

def index(request):
    courses = Course.objects.all()
    user = get_current_user(request)
    print(user)
    return render(request, "pages/homepage.html", {"courses": courses, "user": user})

def login(request):
    return render(request, "pages/login.html")

def login_view(request):
    if request.session.get("user_id"):
        return redirect("index")         

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = User.objects.filter(email=email, is_active=True).first()
        if user and user.check_password(password):
            request.session.cycle_key()
            request.session["user_id"] = user.id

            if request.POST.get("remember"):
                request.session.set_expiry(60 * 60 * 24 * 30)  
            else:
                request.session.set_expiry(0)              

            return redirect("index")

        error = "Invalid email or password."

    return render(request, "pages/login.html", {"error": error})


def logout_view(request):
    request.session.flush()
    return redirect("index")

def signup(request):
    majors = [
        ("computer_science", "Computer Science"),
        ("software_engineering", "Software Engineering"),
        ("telecommunications_networks", "Telecommunications and Networks"),
        ("algebra_cryptography", "Algebra and Cryptography"),
        ("mathematics", "Mathematics"),
        ("probability_statistics", "Probability and Statistics"),
        ("operations_research", "Operations Research"),
        ("intelligent_computer_systems", "Intelligent Computer Systems"),
        ("computer_security", "Computer Systems Security"),
        ("big_data_analytics", "Big Data Analytics"),
        ("electronics", "Electronics"),
        ("automatic_control", "Automatic Control"),
        ("electrical_engineering", "Electrical Engineering"),
        ("telecommunications", "Telecommunications"),
        ("embedded_systems", "Embedded Systems"),
        ("renewable_energy", "Renewable Energy"),
        ("mechanical_engineering", "Mechanical Engineering"),
        ("energy_engineering", "Energy Engineering"),
        ("civil_engineering", "Civil Engineering"),
        ("hydraulics", "Hydraulics"),
        ("physics", "Physics"),
        ("applied_physics", "Applied Physics"),
        ("fundamental_chemistry", "Fundamental Chemistry"),
        ("pharmaceutical_chemistry", "Pharmaceutical Chemistry"),
        ("materials_engineering", "Materials Engineering"),
        ("biochemistry", "Biochemistry"),
        ("microbiology", "Microbiology"),
        ("genetics", "Genetics"),
        ("biotechnology_health", "Biotechnology and Health"),
        ("geophysics", "Geophysics"),
    ]
    return render(request, "pages/signup.html", {"majors":majors})

import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,20}$")
HEARD_FROM = {"friend", "instagram", "facebook", "tiktok", "university", "search", "other"}


def signup_view(request):
    error = None
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        username = request.POST.get("username", "").strip()
        age_raw = request.POST.get("age", "").strip()
        sex = request.POST.get("sex", "N")
        major = request.POST.get("major", "").strip()
        year = request.POST.get("year", "L1")
        heard_from = request.POST.get("heard_from", "")
        phone = request.POST.get("phone", "").strip()

        valid_sex = {c[0] for c in User._meta.get_field("sex").choices}
        valid_year = {c[0] for c in User._meta.get_field("year").choices}

        if password != confirm:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif User.objects.filter(email=email).exists():
            error = "An account with this email already exists."
        elif not USERNAME_RE.match(username):
            error = "Username must be 3-20 characters: letters, numbers, dots or underscores."
        elif User.objects.filter(username__iexact=username).exists():
            error = "This username is already taken."
        elif not (age_raw.isdigit() and 13 <= int(age_raw) <= 120):
            error = "Please enter a valid age (13 or older)."
        elif sex not in valid_sex:
            error = "Invalid gender selection."
        elif not major or len(major) > 100:
            error = "Please enter your major."
        elif year not in valid_year:
            error = "Invalid year selection."
        elif heard_from not in HEARD_FROM:
            error = "Please tell us how you heard about us."
        else:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                age=int(age_raw),
                sex=sex,
                major=major,
                year=year,
                heard_from=heard_from,
                phone=phone,
            )
            user.set_password(password)
            user.save()

            request.session.cycle_key()
            request.session["user_id"] = user.id   # log them in right away
            return redirect("index")

    return render(request, "pages/signup.html", {"error": error})

from django.views.decorators.http import require_GET, require_POST
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

SALT = "signup-email"
LINK_AGE = 60 * 60  # 1 hour


@require_POST
def send_verification(request):
    email = request.POST.get("email", "").strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "error": "Invalid email."}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"ok": False, "error": "This email is already registered."}, status=400)

    token = signing.dumps(email, salt=SALT)
    link = request.build_absolute_uri(reverse("verify_email", args=[token]))

    subject = "Verify your email"

    html_content = render_to_string(
        "emails/verify_email.html",
        {"link": link},
    )

    text_content = (
        "Thanks for signing up!\n\n"
        "Verify your email using the link below:\n"
        f"{link}\n\n"
        "This link is valid for 1 hour."
    )

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
    request.session["pending_email"] = email
    return JsonResponse({"ok": True, "expires_in": LINK_AGE})


def verify_email(request, token):
    try:
        email = signing.loads(token, salt=SALT, max_age=LINK_AGE)
    except signing.BadSignature:  # also covers SignatureExpired
        return HttpResponse("Invalid or expired link.", status=400)
    cache.set(f"verified_email:{email}", True, 60 * 60 * 24)
    return HttpResponse("Email verified. Go back to the signup page to continue.")


@require_GET
def verification_status(request):
    email = request.session.get("pending_email")
    verified = bool(email and cache.get(f"verified_email:{email}"))
    return JsonResponse({"verified": verified})

def account(request):
    user = get_current_user(request)
    return render(request, "pages/account.html", {"user":user})

from django.contrib import messages
from functools import wraps

def login_required_custom(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")
        return view(request, *args, **kwargs)
    return wrapper

@login_required_custom
def account_view(request):
    user = User.objects.get(id=request.session["user_id"])
    form = {}

    if request.method == "POST":
        form = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "email": request.POST.get("email", "").strip().lower(),
        }

        if not form["first_name"] or not form["last_name"]:
            messages.error(request, "First and last name are required.")
        elif not form["email"]:
            messages.error(request, "Email is required.")
        elif User.objects.filter(email=form["email"]).exclude(id=user.id).exists():
            messages.error(request, "Another account already uses this email.")
        else:
            user.first_name = form["first_name"]
            user.last_name = form["last_name"]
            user.email = form["email"]
            user.save()
            messages.success(request, "Your changes have been saved.")
            return redirect("account")   # reload so the whole page shows the new info

    return render(request, "pages/account.html", {"form": form})

def privacy(request):
    return render(request, "pages/privacy-policy.html")

def support(request):
    return render(request, 'pages/support.html')

def success(request):
    return render(request, 'pages/success.html')

def failure(request):
    return render(request, 'pages/failure.html')

def pricing(request):
    return render(request, 'pages/pricing.html')

def robots_txt(request):
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /accounts/
Disallow: /media/private/
Disallow: /static/admin/

Sitemap: https://tela33amek.vercel.app/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

def files(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Exam / Mid-term: flat list, no chapter grouping
    papers = Paper.objects.filter(
        course=course, paper_type__in=["exam", "mid-term"]
    ).order_by("-year")

    # TD / TP: grouped by chapter
    chapters = Chapter.objects.filter(course=course).prefetch_related(
        Prefetch(
            "papers",
            queryset=Paper.objects.filter(paper_type__in=["td", "tp"]).order_by("-year"),
        )
    )

    return render(
        request,
        "pages/filespage.html",
        {"course": course, "papers": papers, "chapters": chapters},
    )

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


def course_chapters(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    chapters = list(course.chapters.values_list("name", flat=True))
    return JsonResponse(chapters, safe=False)


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
course = {course}
year = {year}
establishment = {uni}
teacher = {teacher}
semester = {semester}
major = {major}
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

def send_feedback(request):
    if request.method ==  "POST":
        review = request.POST.get("rating")
        descreption = request.POST.get("description")

        message = f"""
rating: {review}/5
description:
{descreption}
"""     
        send_mail(
                    "New Feedback !!",
                    message,
                    settings.EMAIL_HOST_USER,
                    ["tela33amek@gmail.com"],
                )

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

from pathlib import Path

def view_pdf(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if settings.DEBUG:
        # Serve the file from local storage during development
        try:
            file_path = Path(paper.paper_path.path)
        except (ValueError, NotImplementedError):
            raise Http404("File is not available in local storage.")

        if not file_path.is_file():
            raise Http404("Local file not found.")

        return FileResponse(
            file_path.open("rb"),
            content_type="application/pdf",
        )


    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": paper.paper_path.name,
        },
        ExpiresIn=300,
    )

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
            "https://pay.chargily.net/api/v2/checkouts",
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


CHARGILY_BASE = "https://pay.chargily.net/api/v2"   # live: https://pay.chargily.net/api/v2

def upgrade(request):
    if request.method != "POST":
        return redirect("account")

    user = get_current_user(request)
    if not user:
        return redirect("login")

    try:
        response = requests.post(
            f"{CHARGILY_BASE}/checkouts",
            headers={
                "Authorization": f"Bearer {settings.CHARGILY_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "amount": 100,
                "currency": "dzd",
                "success_url": "https://tela33amek.vercel.app/support/success/",
                "failure_url": "https://tela33amek.vercel.app/support/failure/",
                "webhook_endpoint": "https://tela33amek.vercel.app/chargily/webhooksub/",
                "description": "Tela33amek Premium Plan",
                "metadata": {"user_id": user.id},   # so the webhook knows who paid
            },
            timeout=15,
        )
    except requests.RequestException as e:
        print("CHARGILY ERROR:", e)
        return redirect("account")

    if not response.ok:
        print("STATUS:", response.status_code, "RESPONSE:", response.text)
        return redirect("account")

    checkout_url = response.json()["checkout_url"].replace("http://", "https://")
    return redirect(checkout_url)

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

import hmac, hashlib, json
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def chargily_webhook_sub(request):
    signature = request.headers.get("signature", "")
    expected = hmac.new(
        settings.CHARGILY_SECRET_KEY.encode(), request.body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return HttpResponseBadRequest("invalid signature")

    event = json.loads(request.body)

    if event.get("type") == "checkout.paid":
        user_id = (event["data"].get("metadata") or {}).get("user_id")
        premium = Plan.objects.get(tier="premium")
        Subscription.objects.get_or_create(user_id=user_id, plan=premium)

    return HttpResponse(status=200)

# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Course, Paper


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_paper(request):

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response(
            {"error": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )

    course_name = request.data.get("course", "").strip()

    if not course_name:
        return Response(
            {"error": "Course is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Case-insensitive course lookup
        course = Course.objects.get(name__iexact=course_name)

    except Course.DoesNotExist:
        return Response(
            {"error": f"Course '{course_name}' does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )

    semester = request.data.get("semester", "unknown")
    session = request.data.get("session", "normal")

    if session and session != "unknown":
        semester = f"{semester} - {session}"

    paper_type = request.data.get("paper_type", "exam")

    chapter = None
    chapter_name = request.data.get("chapter", "").strip()

    if paper_type in ("td", "tp") and chapter_name:
        chapter = Chapter.objects.filter(
            course=course, name__iexact=chapter_name
        ).first()

        if chapter is None:
            chapter = Chapter.objects.create(course=course, name=chapter_name)

    paper = Paper.objects.create(
        course=course,
        chapter=chapter,
        major=request.data.get("major", "unknown"),
        year=request.data.get("year", "unknown"),
        semester=semester,
        establishment=request.data.get("establishment", "unknown"),
        teacher=request.data.get("teacher", "unknown"),
        paper_type=paper_type,
        cycle=request.data.get("cycle", "engineer"),
        paper_path=uploaded_file,
    )

    return Response({
        "success": True,
        "id": paper.id,
        "filename": uploaded_file.name
    }, status=status.HTTP_201_CREATED)