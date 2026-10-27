from django.contrib import admin
from django.urls import include, path

from cinema import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("cinema.api_urls")),
    path("health/", views.health, name="health"),
]
