from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from core.models import ProFormaInvoice


def _stripe_secret_key():
    return getattr(settings, "STRIPE_SECRET_KEY", "") or ""


def _stripe_webhook_secret():
    return getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or ""


def _normalize_amount(amount_raw):
    try:
        amount = Decimal(str(amount_raw)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return None
    if amount <= 0:
        return None
    return amount


def _build_checkout_session(request, invoice):
    try:
        import stripe
    except ImportError:
        return None, "Stripe package is not installed."

    secret_key = _stripe_secret_key()
    if not secret_key:
        return None, "Missing STRIPE_SECRET_KEY."

    stripe.api_key = secret_key
    success_url = request.build_absolute_uri("/pay/success/") + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri("/pay/cancel/")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(invoice.amount_eur * 100),
                    "product_data": {
                        "name": "JCW Pro Forma Invoice",
                        "description": invoice.description[:500],
                    },
                },
            }
        ],
        customer_email=invoice.customer_email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"invoice_id": str(invoice.id)},
    )
    return session, None


def _send_proforma_email(invoice, payment_url):
    from_email = getattr(settings, "PROFORMA_FROM_EMAIL", getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@justcodeworks.eu"))
    subject = f"Pro forma invoice #{invoice.id}"
    text_body = (
        f"Hello {invoice.customer_name},\n\n"
        f"Your pro forma invoice is ready.\n\n"
        f"Description: {invoice.description}\n"
        f"Amount: EUR {invoice.amount_eur}\n\n"
        f"Pay here: {payment_url}\n"
    )
    html_body = (
        f"<p>Hello {invoice.customer_name},</p>"
        f"<p>Your pro forma invoice is ready.</p>"
        f"<p><strong>Description:</strong> {invoice.description}</p>"
        f"<p><strong>Amount:</strong> EUR {invoice.amount_eur}</p>"
        f"<p><a href=\"{payment_url}\">Proceed to payment</a></p>"
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[invoice.customer_email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


@require_http_methods(["GET", "POST"])
def pay_invoice(request):
    context = {"invoice": None, "payment_url": None, "error": None}
    if request.method == "POST":
        customer_name = (request.POST.get("name") or "").strip()
        customer_email = (request.POST.get("email") or "").strip()
        description = (request.POST.get("description") or "").strip()
        amount = _normalize_amount(request.POST.get("amount"))

        if not customer_name or not customer_email or not description or amount is None:
            context["error"] = "Please fill all fields with a valid EUR amount."
            return render(request, "core/pay/form.html", context, status=400)

        invoice = ProFormaInvoice.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            description=description,
            amount_eur=amount,
            status=ProFormaInvoice.STATUS_DRAFT,
        )
        session, error = _build_checkout_session(request, invoice)
        if error:
            invoice.status = ProFormaInvoice.STATUS_CANCELED
            invoice.save(update_fields=["status"])
            context["error"] = error
            return render(request, "core/pay/form.html", context, status=500)

        invoice.status = ProFormaInvoice.STATUS_PENDING
        invoice.stripe_checkout_session_id = session.id
        invoice.save(update_fields=["status", "stripe_checkout_session_id"])

        try:
            _send_proforma_email(invoice, session.url)
        except Exception:
            # Keep payment flow working even if email backend is not configured.
            pass

        context["invoice"] = invoice
        context["payment_url"] = session.url
        return render(request, "core/pay/form.html", context)

    return render(request, "core/pay/form.html", context)


def pay_success(request):
    return render(request, "core/pay/success.html")


def pay_cancel(request):
    return render(request, "core/pay/cancel.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    try:
        import stripe
    except ImportError:
        return HttpResponseServerError("Stripe package is not installed.")

    secret_key = _stripe_secret_key()
    webhook_secret = _stripe_webhook_secret()
    if not secret_key or not webhook_secret:
        return HttpResponseBadRequest("Stripe is not configured.")

    stripe.api_key = secret_key
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponseBadRequest("Invalid payload.")
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest("Invalid signature.")

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")
        if session_id:
            invoice = ProFormaInvoice.objects.filter(
                stripe_checkout_session_id=session_id
            ).first()
            if invoice and invoice.status != ProFormaInvoice.STATUS_PAID:
                invoice.status = ProFormaInvoice.STATUS_PAID
                invoice.paid_at = timezone.now()
                invoice.save(update_fields=["status", "paid_at"])

    return HttpResponse(status=200)
