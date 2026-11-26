# Yuhm Yuhm Catering Services (Django)

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations catering
    python manage.py migrate
    python manage.py seed_menu
    python manage.py createsuperuser
    python manage.py runserver

## How a booking and payment works
1. Customer submits the form and lands on a private order page (`/order/<reference>/`).
2. In the admin (Enquiries), set the **Quote (₦)** and send the customer the **Customer payment link**
   (shown on the enquiry; also reachable from their WhatsApp message).
3. The customer pays a deposit (default 50%) or the full amount:
   - **Online (Paystack):** redirected to Paystack, then back. Confirmed automatically by callback and webhook.
   - **Bank transfer:** customer shows their account name, optional proof. In admin go to Payments, select the
     transfer, and run **Confirm selected bank transfers as received** (or Reject).
4. Balance and status ("Unpaid", "Part paid", "Paid in full") update on the order page and in the admin.

## Environment variables
| Name | Purpose |
|---|---|
| WHATSAPP_NUMBER | e.g. 2348012345678 |
| PAYSTACK_SECRET_KEY | sk_test_... while testing, sk_live_... for real money. Leave empty to hide online payment |
| BANK_NAME, BANK_ACCOUNT_NUMBER, BANK_ACCOUNT_NAME | Shown to customers for transfers |
| SITE_URL | Your public address, e.g. https://yuhmyuhm.com (used in admin payment links) |
| DEPOSIT_PERCENT | Default 50 |
| DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_ORIGINS | Production settings |

## Paystack setup`
In the Paystack dashboard (Settings > API Keys & Webhooks) set the webhook URL to
`https://YOUR-DOMAIN/paystack/webhook/`. Test with test keys first.

## Production notes
Run `python manage.py collectstatic --noinput` and serve with `gunicorn yuhm_yuhm.wsgi`.
Proof-of-transfer uploads go to `media/`. Django only serves them when DEBUG=1, so in production serve `media/`
with your web server (or switch to cloud storage) if you want to view them from the admin.
