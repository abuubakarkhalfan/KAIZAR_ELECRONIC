import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


def _tz_number(value):
    digits = re.sub(r"\D", "", value or "")

    if digits.startswith("0"):
        digits = "255" + digits[1:]
    elif digits and not digits.startswith("255"):
        digits = "255" + digits

    return "+" + digits if digits else ""


def send_sms(phone, message):
    username = getattr(settings, "AT_USERNAME", "")
    api_key = getattr(settings, "AT_API_KEY", "")
    recipient = _tz_number(phone)

    if not username or not api_key or not recipient:
        logger.info("SMS skipped: SMS settings are incomplete.")
        return False

    try:
        import africastalking

        africastalking.initialize(username, api_key)
        sender_id = getattr(settings, "AT_SENDER_ID", "") or None

        africastalking.SMS.send(
            message,
            [recipient],
            sender_id=sender_id,
        )
        return True
    except Exception:
        logger.exception("SMS delivery failed.")
        return False


def _items_summary(order):
    return ", ".join(
        f"{item.product_name} x{item.quantity}" for item in order.items.all()
    )


def notify_order_received(order, receipt_url=""):
    items = _items_summary(order)

    admin_message = (
        f"KAIZAR: Oda mpya {str(order.reference)[:8]} kutoka "
        f"{order.customer_name} ({order.phone}); {items}; "
        f"TZS {order.total:,}; {order.status}."
    )

    send_sms(
        getattr(settings, "SMS_ADMIN_PHONE", "0612660381"),
        admin_message,
    )

    if order.payment_method == "HaloPesa":
        customer_message = (
            f"KAIZAR ELOCTRONIC: Oda {str(order.reference)[:8]}, "
            f"jumla TZS {order.total:,}. Lipa HaloPesa 0612660381, "
            f"kisha weka namba ya muamala kwenye risiti. "
            f"PIN iweke kwenye HaloPesa pekee. {receipt_url}"
        )
    else:
        customer_message = (
            f"KAIZAR ELOCTRONIC: Tumepokea oda "
            f"{str(order.reference)[:8]}. Jumla TZS {order.total:,}. "
            "Tutawasiliana nawe."
        )

    send_sms(order.phone, customer_message)


def notify_payment_reference(order):
    message = (
        f"KAIZAR: {order.customer_name} ametuma rejea ya HaloPesa "
        f"{order.payment_reference} kwa oda "
        f"{str(order.reference)[:8]}, TZS {order.total:,}. "
        "Kagua akaunti kabla ya kuthibitisha."
    )

    send_sms(
        getattr(settings, "SMS_ADMIN_PHONE", "0612660381"),
        message,
    )


def notify_payment_confirmed(order):
    items = _items_summary(order)

    send_sms(
        getattr(settings, "SMS_ADMIN_PHONE", "0612660381"),
        f"KAIZAR: Malipo yamethibitishwa. Oda "
        f"{str(order.reference)[:8]} {order.customer_name}; "
        f"{items}; TZS {order.total:,}.",
    )

    send_sms(
        order.phone,
        f"KAIZAR ELOCTRONIC: Malipo ya oda "
        f"{str(order.reference)[:8]} yamethibitishwa. "
        f"Jumla TZS {order.total:,}. Asante kwa kununua kwetu.",
    )
