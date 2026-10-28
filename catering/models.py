from django.db import models


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

    name = models.CharField("Your name", max_length=80)
    event_type = models.CharField("Event type", max_length=30, choices=EVENTS)
    event_date = models.DateField("Event date", null=True, blank=True)
    guests = models.PositiveIntegerField("Number of guests", null=True, blank=True)
    cuisine = models.CharField("Cuisine you want", max_length=30, choices=CUISINES)
    notes = models.TextField("Anything else?", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} ({self.event_type})"

    def whatsapp_message(self):
        date = self.event_date.strftime("%d %b %Y") if self.event_date else "a date not yet fixed"
        guests = self.guests or "an unknown number of"
        return (f"Hello Yuhm Yuhm! I’m {self.name}. I’d like a quote for a {self.event_type} "
                f"on {date} for {guests} guests. Cuisine: {self.cuisine}. Notes: {self.notes}")
