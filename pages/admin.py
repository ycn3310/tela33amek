from django.contrib import admin
from .models import *
from django.urls import path
from django.http import JsonResponse
# Register your models here.
admin.site.register(Course)
admin.site.register(Donation)
admin.site.register(Chapter)

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    search_fields = ["id"]

    class Media:
        js = ("admin/js/paper_chapters.js",)

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "chapters-for-course/",
                self.admin_site.admin_view(self.chapters_for_course),
                name="chapters-for-course",
            ),
        ]

        return custom_urls + urls

    def chapters_for_course(self, request):
        course_id = request.GET.get("course_id")

        chapters = Chapter.objects.filter(
            course_id=course_id
        ).values("id", "name")

        return JsonResponse(list(chapters), safe=False)