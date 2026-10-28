from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Yuhm Yuhm Catering Services"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catering.urls")),
]
