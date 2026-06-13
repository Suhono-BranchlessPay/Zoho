"""Map Zoho Books webhook documents to BranchlessPay anchor payload."""

from datetime import datetime, timezone
from typing import Any

EVENT_TYPE_MAP = {
    "invoice.created": "zoho_invoice_created",
    "invoice.updated": "zoho_invoice_updated",
    "payment.created": "zoho_payment_received",
    "bill.created": "zoho_bill_created",
    "creditnote.created": "zoho_creditnote_created",
    "purchaseorder.created": "zoho_po_created",
}

DOCUMENT_TYPE_MAP = {
    "invoice.created": "Invoice",
    "invoice.updated": "Invoice",
    "payment.created": "Payment",
    "bill.created": "Bill",
    "creditnote.created": "Credit Note",
    "purchaseorder.created": "Purchase Order",
}

ERP_DISPLAY_LABEL = "Zoho Books"


def map_event_type(zoho_event: str) -> str:
    mapped = EVENT_TYPE_MAP.get(zoho_event)
    if not mapped:
        raise ValueError("Unsupported Zoho event: %s" % zoho_event)
    return mapped


def normalize_to_bp_payload(
    zoho_event: str,
    document: dict[str, Any],
    *,
    organization_id: str = "",
    org_name: str = "",
    org_address: str = "",
    region: str = "US",
) -> dict[str, Any]:
    event_type = map_event_type(zoho_event)
    document_type = DOCUMENT_TYPE_MAP[zoho_event]
    amount, currency = _extract_amount(document, zoho_event)
    reference_id = _extract_reference_id(document, zoho_event)
    contact_name = _extract_contact_name(document, zoho_event)
    status = str(document.get("status") or "unknown").lower()
    business = org_name or str(document.get("company_name") or "Zoho Organisation")
    address = org_address or str(document.get("company_address") or "")
    voucher_date = _extract_voucher_date(document, zoho_event)
    timestamp = _extract_timestamp(document, voucher_date)
    resolved_org_id = organization_id or str(document.get("organization_id") or "")

    metadata: dict[str, Any] = {
        "erp": "zoho_books",
        "erp_system": ERP_DISPLAY_LABEL,
        "company_name": business,
        "business_name": business,
        "business_address": address,
        "organization_id": resolved_org_id,
        "document_type": document_type,
        "contact_name": contact_name,
        "status": status,
        "zoho_id": _extract_zoho_id(document, zoho_event),
        "zoho_event": zoho_event,
        "voucher_date": voucher_date,
        "create_date": voucher_date,
        "currency_code": currency,
        "region": region.upper(),
        "amount_enriched": True,
    }

    if zoho_event.startswith("invoice."):
        metadata["invoice_number"] = reference_id
        metadata["due_date"] = _extract_due_date(document)
    elif zoho_event.startswith("payment."):
        metadata["payment_date"] = voucher_date
    elif zoho_event.startswith("bill."):
        metadata["bill_number"] = reference_id
        metadata["due_date"] = _extract_due_date(document)
    elif zoho_event.startswith("creditnote."):
        metadata["creditnote_number"] = reference_id
    elif zoho_event.startswith("purchaseorder."):
        metadata["purchaseorder_number"] = reference_id

    payload: dict[str, Any] = {
        "event_type": event_type,
        "reference_id": reference_id,
        "amount": amount,
        "currency": currency,
        "voucher_date": voucher_date,
        "timestamp": timestamp,
        "metadata": metadata,
    }

    if business:
        payload["business_name"] = business
    if address:
        payload["business_address"] = address
    if resolved_org_id:
        payload["organization_id"] = resolved_org_id
    payload["erp_system"] = ERP_DISPLAY_LABEL

    return payload


def _parse_amount(raw: Any) -> float:
    if raw is None:
        return 0.0
    text = str(raw).strip().replace(",", "")
    if not text:
        return 0.0
    return float(text)


def _extract_amount(document: dict[str, Any], event_type: str) -> tuple[float, str]:
    currency = str(
        document.get("currency_code") or document.get("currency") or "USD"
    ).upper()

    for key in ("total", "amount", "balance", "bcy_total"):
        if document.get(key) is not None:
            return _parse_amount(document[key]), currency

    return 0.0, currency


def _extract_reference_id(document: dict[str, Any], event_type: str) -> str:
    ref_map = {
        "invoice.created": ("invoice_number", "invoice_id"),
        "invoice.updated": ("invoice_number", "invoice_id"),
        "payment.created": ("reference_number", "payment_id"),
        "bill.created": ("bill_number", "bill_id"),
        "creditnote.created": ("creditnote_number", "creditnote_id"),
        "purchaseorder.created": ("purchaseorder_number", "purchaseorder_id"),
    }
    for key in ref_map.get(event_type, ("id",)):
        value = document.get(key)
        if value:
            return str(value)
    return "unknown"


def _extract_contact_name(document: dict[str, Any], event_type: str) -> str:
    for key in (
        "customer_name",
        "vendor_name",
        "contact_name",
        "customer",
        "vendor",
    ):
        value = document.get(key)
        if value:
            return str(value)
    return "Unknown"


def _extract_zoho_id(document: dict[str, Any], event_type: str) -> str:
    for suffix in (
        "invoice_id",
        "payment_id",
        "bill_id",
        "creditnote_id",
        "purchaseorder_id",
    ):
        value = document.get(suffix)
        if value:
            return str(value)
    return str(document.get("id") or "")


def _extract_voucher_date(document: dict[str, Any], event_type: str) -> str:
    keys = ("date", "created_time", "payment_date", "order_date")
    for key in keys:
        value = document.get(key)
        if value:
            return _date_only(str(value))
    return ""


def _extract_due_date(document: dict[str, Any]) -> str:
    value = document.get("due_date")
    if value:
        return _date_only(str(value))
    return ""


def _extract_timestamp(document: dict[str, Any], voucher_date: str) -> str:
    for key in ("created_time", "last_modified_time", "date"):
        value = document.get(key)
        if value:
            text = str(value)
            if "T" in text:
                return text.replace(" ", "T")
            if voucher_date:
                return "%sT00:00:00Z" % _date_only(text)
    if voucher_date:
        return "%sT00:00:00Z" % voucher_date
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_only(value: str) -> str:
    return value.split("T")[0].split(" ")[0]
