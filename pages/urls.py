from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('papers/<int:course_id>/', views.files, name='papers'),
    path("suggestions/", views.suggestions, name="suggestions"),
    path("report/<int:paper_id>/", views.report, name="report"),
    path("send_paper", views.send_paper, name="send_paper"),
    path("download/<int:paper_id>/", views.view_pdf, name="view_pdf"),
    path("support/", views.support, name="support"),
    path("support/donate/", views.make_donation, name="donation"),
    path("support/success/", views.success, name="success"),
    path("support/failure/", views.failure, name="failure"),
    path("chargily/webhook", views.chargily_webhook, name="chargily_webhook"),
    path("feedback/", views.send_feedback, name="feedback"),
]
