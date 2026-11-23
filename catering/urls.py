from django.urls import path
from . import views

app_name = "catering"
urlpatterns = [
    path("", views.home, name="home"),
    path("order/<slug:reference>/", views.order_detail, name="order"),
    path("order/<slug:reference>/pay-online/", views.pay_online, name="pay_online"),
    path("order/<slug:reference>/pay-transfer/", views.pay_transfer, name="pay_transfer"),
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"),
    path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
]
