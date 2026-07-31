from django.db import models

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=256)
    logo_path = models.CharField(max_length=256)

class Paper(models.Model):
    course = models.CharField(max_length=256)
    major = models.CharField(max_length=256)
    year = models.CharField(max_length=9)
    semester = models.CharField(max_length=30)
    establishment = models.CharField(max_length=256)
    teacher = models.CharField(max_length=256)
   
