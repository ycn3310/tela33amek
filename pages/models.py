from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from datetime import timedelta
from django.utils import timezone

class Course(models.Model):
    name = models.CharField(max_length=256)
    logo_path = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    name = models.CharField(max_length=256)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course} - {self.name} : {self.order}"


class Paper(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="papers")
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        related_name="papers",
        null=True,
        blank=True,
        help_text="Only used for TD / TP papers.",
    )
    major = models.CharField(max_length=256, default="unknown")
    year = models.CharField(max_length=9, default="unknown")
    semester = models.CharField(max_length=30, default="unknown")
    establishment = models.CharField(max_length=256, default="unknown")
    teacher = models.CharField(max_length=256, default="unknown")
    paper_path = models.FileField(upload_to='papers/%y/%m/%d', null=True, blank=True)

    PAPER_TYPES = [
        ("exam", "Exam"),
        ("mid-term", "Mid-term"),
        ("td", "TD"),
        ("tp", "TP"),
    ]

    CYCLES = [
        ("license", "License"),
        ("master", "Master"),
        ("engineer", "Engineer"),
    ]

    paper_type = models.CharField(
        max_length=20,
        choices=PAPER_TYPES,
        default="exam",
    )

    cycle = models.CharField(
        max_length=20,
        choices=CYCLES,
        default="engineer",
    )


    def __str__(self):
        return f"id:{self.id} | {self.course} ({self.year})"


class Donation(models.Model):
    checkout_id = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} da - {self.status}"


class Plan(models.Model):
    class Tier(models.TextChoices):
        BASIC = "basic", "Basic"
        PREMIUM = "premium", "Premium"

    name = models.CharField(max_length=50, unique=True)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.BASIC)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(starts_at__lte=now, expires_at__gt=now)


class Subscription(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SubscriptionQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.starts_at + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.starts_at <= timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.user} - {self.plan} (until {self.expires_at:%Y-%m-%d})"

class User(models.Model):

    Year = [
        ("L1", "Lisence 1"),
        ("L2", "Lisence 2"),
        ("L3", "Lisence 3"),
        ("M1", "Master 1"),
        ("M2", "Master 2"),
        ("ing1", "Ingenieur 1"),
        ("ing2", "Ingenieur 2"),
        ("ing3", "Ingenieur 3"),
        ("ing4", "Ingenieur 4"),
        ("ing5", "Ingenieur 5"),
    ]

    username = models.CharField(max_length=50, default="null")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    password = models.CharField(max_length=128) 
    age = models.PositiveIntegerField(default=18)
    major = models.CharField(default="nothing")
    sex = models.CharField(choices=[("N","Not specified"),("M","Male"), ("F", "Female")], default="N")
    year = models.CharField(choices = Year, default="L1")
    heard_from = models.CharField(max_length=20, blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def current_subscription(self):
        return (
            self.subscriptions.active()
            .select_related("plan")
            .order_by("-expires_at")
            .first()
        )

    @property
    def is_premium(self):
        return self.subscriptions.active().filter(plan__tier=Plan.Tier.PREMIUM).exists()

    def __str__(self):
        status = "Premium" if self.is_premium else "Basic"
        return f"{self.first_name} {self.last_name} ({status})"