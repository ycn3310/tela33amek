from django.db import models



class Course(models.Model):
    name = models.CharField(max_length=256)
    logo_path = models.FileField(upload_to='course_icons')

    def __str__(self):
        return self.name

    
class Paper(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="papers")
    major = models.CharField(max_length=256)
    year = models.CharField(max_length=9)
    semester = models.CharField(max_length=30)
    establishment = models.CharField(max_length=256)
    teacher = models.CharField(max_length=256)
    paper_path = models.FileField(upload_to='papers/%y/%m/%d', null=True, blank=True)

    

    def __str__(self):
        return f"{self.major} / {self.course}:[{self.year}]"



   
