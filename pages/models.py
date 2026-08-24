from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=256)
    logo_path = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name

class Paper(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="papers")
    major = models.CharField(max_length=256, default="unknown")
    year = models.CharField(max_length=9, default="unknown")
    semester = models.CharField(max_length=30, default="unknown")
    establishment = models.CharField(max_length=256, default="unknown")
    teacher = models.CharField(max_length=256, default="unknown")
    paper_path = models.FileField(upload_to='papers/%y/%m/%d', null=True, blank=True)

    PAPER_TYPES = [
        ("exam", "Exam"),
        ("mid-term", "Mid-term"),
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


   
