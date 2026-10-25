from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, CourseSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "courses": CourseSitemap,
}

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('papers/<int:course_id>/', views.files, name='papers'),
    path("suggestions/", views.suggestions, name="suggestions"),
    path("papers/<int:course_id>/chapters/", views.course_chapters, name="course_chapters"),
    path("report/<int:paper_id>/", views.report, name="report"),
    path("send_paper", views.send_paper, name="send_paper"),
    path("download/<int:paper_id>/", views.view_pdf, name="view_pdf"),
    path("support/", views.support, name="support"),
    path("support/donate/", views.make_donation, name="donation"),
    path("support/success/", views.success, name="success"),
    path("support/failure/", views.failure, name="failure"),
    path("chargily/webhook", views.chargily_webhook, name="chargily_webhook"),
    path("feedback/", views.send_feedback, name="feedback"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),
    path("robots.txt", views.robots_txt),
    path("privacy&policy", views.privacy, name="privacy"),
    path("api/upload-paper/", views.upload_paper, name ="upload_paper"),
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("signup_view", views.signup_view, name="signupview"),
    path("login_view", views.login_view, name="loginview"),
    path("logout_view", views.logout_view, name="logoutview"),
    path("account", views.account, name="account"),
    path("account_view", views.account_view, name="accountview"),
    path("signup/send-verification/", views.send_verification, name="send_verification"),
    path("signup/verification-status/", views.verification_status, name="verification_status"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
]