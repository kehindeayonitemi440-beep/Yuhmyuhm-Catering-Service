from django.conf import settings
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Dish, Enquiry, Payment, Testimonial


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


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ("reference", "method", "amount", "status", "sender_name", "proof", "paid_at")
    readonly_fields = ("reference", "method", "amount", "status", "sender_name", "proof", "paid_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "event_date", "guests", "quoted_amount",
                    "amount_paid", "payment_status", "created_at", "contacted")
    list_filter = ("event_type", "cuisine", "contacted")
    list_editable = ("contacted",)
    search_fields = ("name", "email", "phone", "reference")
    date_hierarchy = "created_at"
    readonly_fields = ("reference", "payment_link", "amount_paid", "balance_due", "payment_status")
    inlines = [PaymentInline]

    @admin.display(description="Customer payment link")
    def payment_link(self, obj):
        if not obj.pk:
            return "-"
        url = settings.SITE_URL.rstrip("/") + reverse("catering:order", args=[obj.reference])
        return format_html('<a href="{0}" target="_blank">{0}</a><br>Send this link to the customer after setting the quote.', url)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "enquiry", "method", "amount", "status", "sender_name", "created_at")
    list_filter = ("status", "method")
    search_fields = ("reference", "enquiry__name", "sender_name")
    readonly_fields = ("reference", "created_at", "paid_at")
    actions = ["confirm_transfers", "reject_transfers"]

    @admin.action(description="Confirm selected bank transfers as received")
    def confirm_transfers(self, request, queryset):
        n = 0
        for p in queryset.filter(method=Payment.TRANSFER).exclude(status=Payment.SUCCESS):
            n += p.mark_success()
        self.message_user(request, f"{n} transfer(s) confirmed.", messages.SUCCESS)

    @admin.action(description="Reject selected bank transfers (not received)")
    def reject_transfers(self, request, queryset):
        n = queryset.filter(method=Payment.TRANSFER, status=Payment.AWAITING).update(status=Payment.FAILED)
        self.message_user(request, f"{n} transfer(s) rejected.", messages.WARNING)
