from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Course)
admin.site.register(Donation)
admin.site.register(Chapter)

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    search_fields = ["id"]