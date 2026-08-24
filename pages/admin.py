from django.contrib import admin
from .models import Course, Paper, Donation
# Register your models here.
admin.site.register(Course)
admin.site.register(Donation)
admin.site.register(Paper)

class PaperAdmin(admin.ModelAdmin):
    search_fields = ["id"]