from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('papers/<int:course_id>/', views.files, name='papers'),
    path("pdf/<int:paper_id>/", views.view_pdf, name="view_pdf"),
]
