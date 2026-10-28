from django.urls import path
from . import views

app_name = "catering"
urlpatterns = [path("", views.home, name="home")]
