from urllib.parse import quote

from django.conf import settings
from django.shortcuts import redirect, render

from .forms import EnquiryForm
from .models import Dish, Testimonial


def home(request):
    form = EnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        enquiry = form.save()
        url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(enquiry.whatsapp_message())}"
        return redirect(url)

    dishes = Dish.objects.filter(is_active=True)
    return render(request, "catering/home.html", {
        "form": form,
        "continental": dishes.filter(cuisine=Dish.CONTINENTAL),
        "intercontinental": dishes.filter(cuisine=Dish.INTERCONTINENTAL),
        "testimonials": Testimonial.objects.filter(is_active=True),
    })
