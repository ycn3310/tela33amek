from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Course

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["index"]

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Course.objects.all()

    def location(self, course):
        return reverse("papers", args=[course.id])