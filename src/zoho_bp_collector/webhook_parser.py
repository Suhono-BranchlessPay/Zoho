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

_MODULE_DETECTORS = (
    ("invoice.created", ("invoice_id",), ("invoice",)),
    ("invoice.updated", ("invoice_id",), ("invoice",)),
    ("payment.created", ("payment_id",), ("payment",)),
    ("bill.created", ("bill_id",), ("bill",)),
    ("creditnote.created", ("creditnote_id",), ("creditnote",)),
    ("purchaseorder.created", ("purchaseorder_id",), ("purchaseorder",)),
)


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    resource_id: str
    organization_id: str
    document: dict[str, Any]
    raw: dict[str, Any]


def parse_webhook_event(
    body: dict[str, Any],
    *,
    default_organization_id: str = "",
    default_event_type: str = "",
) -> WebhookEvent:
    if not isinstance(body, dict):
        raise ValueError("Webhook body must be a JSON object")

    event_type = _resolve_event_type(body, default_event_type)
    organization_id = _resolve_organization_id(body, default_organization_id)
    document = _resolve_document(body, event_type)

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


def _resolve_event_type(body: dict[str, Any], default_event_type: str) -> str:
    for key in ("event", "event_type", "action", "trigger"):
        value = str(body.get(key) or "").strip()
        if value in ANCHOR_EVENTS:
            return value
        normalized = value.lower().replace(" ", "_")
        if normalized in ANCHOR_EVENTS:
            return normalized

    entity = str(body.get("entity") or body.get("module") or "").strip().lower()
    if entity == "invoice":
        status = str(body.get("status") or "").lower()
        if status in ("sent", "paid", "overdue", "partially_paid", "void"):
            return "invoice.updated"
        return "invoice.created"
    if entity == "customer_payment":
        return "payment.created"
    if entity == "bill":
        return "bill.created"
    if entity in ("creditnote", "credit_note"):
        return "creditnote.created"
    if entity in ("purchaseorder", "purchase_order"):
        return "purchaseorder.created"

    for event_type, id_keys, nested_keys in _MODULE_DETECTORS:
        if any(body.get(key) for key in id_keys):
            if event_type.endswith(".updated") and default_event_type:
                return default_event_type if default_event_type in ANCHOR_EVENTS else event_type
            if event_type.endswith(".created"):
                return event_type
        for nested in nested_keys:
            nested_doc = body.get(nested)
            if isinstance(nested_doc, dict) and any(nested_doc.get(key) for key in id_keys):
                return event_type

    if default_event_type in ANCHOR_EVENTS:
        return default_event_type

    raise ValueError("Missing Zoho event field")


def _resolve_organization_id(body: dict[str, Any], default_organization_id: str) -> str:
    for key in ("organization_id", "org_id", "organizationId"):
        value = str(body.get(key) or "").strip()
        if value:
            return value
    return str(default_organization_id or "").strip() or ""


def _resolve_document(body: dict[str, Any], event_type: str) -> dict[str, Any]:
    data = body.get("data")
    if isinstance(data, dict):
        data_key = _DATA_KEY_MAP[event_type]
        document = data.get(data_key)
        if isinstance(document, dict):
            return document

    nested_key = _DATA_KEY_MAP[event_type]
    nested = body.get(nested_key)
    if isinstance(nested, dict):
        return nested

    id_keys = _id_keys_for_event(event_type)
    if any(body.get(key) for key in id_keys):
        return dict(body)

    raise ValueError("Missing Zoho document payload")


def _id_keys_for_event(event_type: str) -> tuple[str, ...]:
    mapping = {
        "invoice.created": ("invoice_id", "invoice_number"),
        "invoice.updated": ("invoice_id", "invoice_number"),
        "payment.created": ("payment_id",),
        "bill.created": ("bill_id", "bill_number"),
        "creditnote.created": ("creditnote_id", "creditnote_number"),
        "purchaseorder.created": ("purchaseorder_id", "purchaseorder_number"),
    }
    return mapping.get(event_type, ("id",))


def _extract_resource_id(document: dict[str, Any], event_type: str) -> str:
    for key in _id_keys_for_event(event_type):
        value = document.get(key)
        if value:
            return str(value)
    fallback = document.get("id")
    return str(fallback) if fallback else ""
