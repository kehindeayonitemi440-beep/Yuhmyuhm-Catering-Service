import secrets

import catering.models
from django.db import migrations, models


def populate_enquiry_references(apps, schema_editor):
    Enquiry = apps.get_model("catering", "Enquiry")
    enquiries = Enquiry.objects.using(schema_editor.connection.alias)

    for enquiry in enquiries.filter(reference__isnull=True).iterator():
        reference = secrets.token_urlsafe(9)
        while enquiries.filter(reference=reference).exists():
            reference = secrets.token_urlsafe(9)
        enquiries.filter(pk=enquiry.pk).update(reference=reference)


class Migration(migrations.Migration):

    dependencies = [
        ("catering", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="enquiry",
            name="email",
            field=models.EmailField(max_length=254, null=True, verbose_name="Email"),
        ),
        migrations.AddField(
            model_name="enquiry",
            name="phone",
            field=models.CharField(
                blank=True,
                default="",
                max_length=25,
                verbose_name="Phone (optional)",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="enquiry",
            name="quoted_amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Set this to open payment on the customer's order page.",
                max_digits=12,
                null=True,
                verbose_name="Quote (₦)",
            ),
        ),
        migrations.AddField(
            model_name="enquiry",
            name="reference",
            field=models.SlugField(max_length=20, null=True),
        ),
        migrations.RunPython(populate_enquiry_references, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="enquiry",
            name="reference",
            field=models.SlugField(
                default=catering.models.new_order_ref,
                editable=False,
                max_length=20,
                unique=True,
            ),
        ),
    ]
