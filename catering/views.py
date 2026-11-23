import json
from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import paystack
from .forms import EnquiryForm, TransferForm
from .models import Dish, Enquiry, Payment, Testimonial


def home(request):
    form = EnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        enquiry = form.save()
        return redirect("catering:order", reference=enquiry.reference)

    dishes = Dish.objects.filter(is_active=True)
    return render(request, "catering/home.html", {
        "form": form,
        "continental": dishes.filter(cuisine=Dish.CONTINENTAL),
        "intercontinental": dishes.filter(cuisine=Dish.INTERCONTINENTAL),
        "testimonials": Testimonial.objects.filter(is_active=True),
    })


def payment_options(enquiry):
    """What the customer may pay now. Amounts always come from the server, never the browser."""
    balance = enquiry.balance_due
    if not balance:
        return []
    options = []
    if enquiry.amount_paid == 0:
        deposit = (enquiry.quoted_amount * settings.DEPOSIT_PERCENT / 100).quantize(Decimal("1"))
        if 0 < deposit < balance:
            options.append(("deposit", f"Deposit ({settings.DEPOSIT_PERCENT}%)", deposit))
    options.append(("full", "Full balance" if enquiry.amount_paid else "Pay in full", balance))
    return options


def _chosen_amount(enquiry, key):
    return {k: amt for k, _, amt in payment_options(enquiry)}.get(key)


def order_detail(request, reference):
    enquiry = get_object_or_404(Enquiry, reference=reference)
    order_url = request.build_absolute_uri(request.path)
    wa_text = (f"Hello Yuhm Yuhm! I’m {enquiry.name}. I’d like a quote for a {enquiry.event_type} "
               f"for {enquiry.guests or 'an unknown number of'} guests. Cuisine: {enquiry.cuisine}. "
               f"My order page: {order_url}")
    return render(request, "catering/order_detail.html", {
        "enquiry": enquiry,
        "options": payment_options(enquiry),
        "history": enquiry.payments.filter(status__in=[Payment.SUCCESS, Payment.AWAITING]),
        "transfer_form": TransferForm(),
        "paystack_enabled": bool(settings.PAYSTACK_SECRET_KEY),
        "bank": {"name": settings.BANK_NAME, "number": settings.BANK_ACCOUNT_NUMBER,
                 "account": settings.BANK_ACCOUNT_NAME},
        "wa_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(wa_text)}",
    })


@require_POST
def pay_online(request, reference):
    enquiry = get_object_or_404(Enquiry, reference=reference)
    amount = _chosen_amount(enquiry, request.POST.get("option"))
    if amount is None:
        messages.error(request, "Please choose how much you want to pay.")
        return redirect("catering:order", reference=reference)
    payment = Payment.objects.create(enquiry=enquiry, method=Payment.PAYSTACK, amount=amount)
    try:
        url = paystack.initialize(payment, request.build_absolute_uri(reverse("catering:paystack_callback")))
    except paystack.PaystackError:
        payment.status = Payment.FAILED
        payment.save(update_fields=["status"])
        messages.error(request, "We couldn’t start the online payment. Please try again or pay by transfer.")
        return redirect("catering:order", reference=reference)
    return redirect(url)


@require_POST
def pay_transfer(request, reference):
    enquiry = get_object_or_404(Enquiry, reference=reference)
    amount = _chosen_amount(enquiry, request.POST.get("option"))
    form = TransferForm(request.POST, request.FILES)
    if amount is None or not form.is_valid():
        messages.error(request, "Please choose an amount and tell us the name on the account you paid from. "
                                + " ".join(e for errs in form.errors.values() for e in errs))
        return redirect("catering:order", reference=reference)
    payment = form.save(commit=False)
    payment.enquiry, payment.method, payment.amount = enquiry, Payment.TRANSFER, amount
    payment.status = Payment.AWAITING
    payment.save()
    messages.success(request, "Thank you! We’ll confirm your transfer as soon as we see it.")
    return redirect("catering:order", reference=reference)


def paystack_callback(request):
    reference = request.GET.get("reference", "")
    payment = paystack.settle(reference)
    if payment is None:
        return redirect("catering:home")
    if payment.status == Payment.SUCCESS:
        messages.success(request, f"Payment of ₦{payment.amount:,.2f} received. Thank you!")
    else:
        messages.error(request, "We couldn’t confirm that payment. If you were charged, contact us with your reference "
                                f"{payment.reference}.")
    return redirect("catering:order", reference=payment.enquiry.reference)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    if not paystack.valid_signature(request.body, request.headers.get("X-Paystack-Signature", "")):
        return HttpResponse(status=400)
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)
    if event.get("event") == "charge.success":
        paystack.settle(event.get("data", {}).get("reference", ""))
    return HttpResponse(status=200)
