"""Parse Zoho Books webhook JSON payload."""

from dataclasses import dataclass
from typing import Any


ANCHOR_EVENTS = frozenset(
    {
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "bill.created",
        "creditnote.created",
        "purchaseorder.created",
    }
)

_DATA_KEY_MAP = {
    "invoice.created": "invoice",
    "invoice.updated": "invoice",
    "payment.created": "payment",
    "bill.created": "bill",
    "creditnote.created": "creditnote",
    "purchaseorder.created": "purchaseorder",
}


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    resource_id: str
    organization_id: str
    document: dict[str, Any]
    raw: dict[str, Any]


def parse_webhook_event(body: dict[str, Any]) -> WebhookEvent:
    event_type = str(body.get("event") or "").strip()
    if not event_type:
        raise ValueError("Missing Zoho event field")
    if event_type not in ANCHOR_EVENTS:
        raise ValueError("Unsupported Zoho event: %s" % event_type)

    organization_id = str(body.get("organization_id") or "").strip()
    if not organization_id:
        raise ValueError("Missing organization_id")

    data = body.get("data")
    if not isinstance(data, dict):
        raise ValueError("Missing Zoho data object")

    data_key = _DATA_KEY_MAP[event_type]
    document = data.get(data_key)
    if not isinstance(document, dict):
        raise ValueError("Missing Zoho data.%s object" % data_key)

    resource_id = _extract_resource_id(document, event_type)
    if not resource_id:
        raise ValueError("Missing resource id in Zoho payload")

    return WebhookEvent(
        event_type=event_type,
        resource_id=resource_id,
        organization_id=organization_id,
        document=document,
        raw=body,
    )


def _extract_resource_id(document: dict[str, Any], event_type: str) -> str:
    id_keys = {
        "invoice.created": ("invoice_id",),
        "invoice.updated": ("invoice_id",),
        "payment.created": ("payment_id",),
        "bill.created": ("bill_id",),
        "creditnote.created": ("creditnote_id",),
        "purchaseorder.created": ("purchaseorder_id",),
    }
    for key in id_keys.get(event_type, ("id",)):
        value = document.get(key)
        if value:
            return str(value)
    fallback = document.get("id")
    return str(fallback) if fallback else ""
