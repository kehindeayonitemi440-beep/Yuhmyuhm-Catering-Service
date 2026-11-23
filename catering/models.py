import secrets
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone


def new_order_ref():
    return secrets.token_urlsafe(9)


def new_payment_ref():
    return "YY-" + secrets.token_hex(6).upper()


class Dish(models.Model):
    CONTINENTAL = "con"
    INTERCONTINENTAL = "int"
    CUISINES = [(CONTINENTAL, "Continental"), (INTERCONTINENTAL, "Intercontinental")]

    name = models.CharField(max_length=80)
    description = models.CharField(max_length=160)
    cuisine = models.CharField(max_length=3, choices=CUISINES)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")

    class Meta:
        ordering = ["cuisine", "position", "name"]
        verbose_name_plural = "dishes"

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    quote = models.CharField(max_length=220)
    author = models.CharField(max_length=80, help_text="e.g. Wedding client")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.author}: {self.quote[:40]}"


class Enquiry(models.Model):
    EVENTS = [(e, e) for e in ("Wedding", "Corporate event", "Birthday or party", "Other")]
    CUISINES = [(c, c) for c in ("Continental", "Intercontinental", "A mix of both")]

    reference = models.SlugField(max_length=20, unique=True, default=new_order_ref, editable=False)
    name = models.CharField("Your name", max_length=80)
    email = models.EmailField("Email")
    phone = models.CharField("Phone (optional)", max_length=25, blank=True)
    event_type = models.CharField("Event type", max_length=30, choices=EVENTS)
    event_date = models.DateField("Event date", null=True, blank=True)
    guests = models.PositiveIntegerField("Number of guests", null=True, blank=True)
    cuisine = models.CharField("Cuisine you want", max_length=30, choices=CUISINES)
    notes = models.TextField("Anything else?", blank=True)
    quoted_amount = models.DecimalField("Quote (₦)", max_digits=12, decimal_places=2, null=True, blank=True,
                                        help_text="Set this to open payment on the customer's order page.")
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} ({self.event_type})"

    @property
    def amount_paid(self):
        total = self.payments.filter(status=Payment.SUCCESS).aggregate(t=Sum("amount"))["t"]
        return total or Decimal("0")

    @property
    def balance_due(self):
        if self.quoted_amount is None:
            return None
        return max(self.quoted_amount - self.amount_paid, Decimal("0"))

    @property
    def payment_status(self):
        if self.quoted_amount is None:
            return "Awaiting quote"
        if self.balance_due == 0:
            return "Paid in full"
        return "Part paid" if self.amount_paid > 0 else "Unpaid"


class Payment(models.Model):
    PAYSTACK, TRANSFER = "paystack", "transfer"
    METHODS = [(PAYSTACK, "Online (Paystack)"), (TRANSFER, "Bank transfer")]
    PENDING, AWAITING, SUCCESS, FAILED = "pending", "awaiting", "success", "failed"
    STATUSES = [(PENDING, "Pending"), (AWAITING, "Awaiting confirmation"),
                (SUCCESS, "Successful"), (FAILED, "Failed or rejected")]

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=10, choices=METHODS)
    amount = models.DecimalField("Amount (₦)", max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    reference = models.CharField(max_length=30, unique=True, default=new_payment_ref, editable=False)
    sender_name = models.CharField("Account name used", max_length=80, blank=True)
    transfer_note = models.CharField("Transfer reference or note", max_length=120, blank=True)
    proof = models.FileField("Proof of transfer", upload_to="proofs/%Y/%m/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} ₦{self.amount} ({self.get_status_display()})"

    def mark_success(self):
        """Idempotent: returns True only the first time it flips to success."""
        with transaction.atomic():
            p = Payment.objects.select_for_update().get(pk=self.pk)
            if p.status == self.SUCCESS:
                return False
            p.status, p.paid_at = self.SUCCESS, timezone.now()
            p.save(update_fields=["status", "paid_at"])
        self.status, self.paid_at = p.status, p.paid_at
        return True
