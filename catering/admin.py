from django.contrib import admin
from .models import Dish, Enquiry, Testimonial


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "cuisine", "is_popular", "is_active", "position")
    list_filter = ("cuisine", "is_active", "is_popular")
    list_editable = ("is_popular", "is_active", "position")
    search_fields = ("name",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "quote", "is_active")
    list_editable = ("is_active",)


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "event_date", "guests", "cuisine", "created_at", "contacted")
    list_filter = ("event_type", "cuisine", "contacted")
    list_editable = ("contacted",)
    date_hierarchy = "created_at"
