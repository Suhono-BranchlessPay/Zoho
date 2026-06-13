"""Zoho webhook parser tests."""

import pytest

from zoho_bp_collector.webhook_parser import parse_webhook_event


def _invoice_body(event: str = "invoice.created"):
    return {
        "event": event,
        "organization_id": "org-123",
        "data": {
            "invoice": {
                "invoice_id": "inv-001",
                "invoice_number": "INV-000001",
                "customer_name": "John Smith",
                "total": 1500.0,
                "currency_code": "USD",
                "date": "2026-06-13",
                "due_date": "2026-07-13",
                "status": "draft",
            }
        },
    }


@pytest.mark.parametrize(
    "event,data_key,id_field,number_field",
    [
        ("payment.created", "payment", "payment_id", "reference_number"),
        ("bill.created", "bill", "bill_id", "bill_number"),
        ("creditnote.created", "creditnote", "creditnote_id", "creditnote_number"),
        ("purchaseorder.created", "purchaseorder", "purchaseorder_id", "purchaseorder_number"),
    ],
)
def test_parse_all_event_types(event, data_key, id_field, number_field):
    body = {
        "event": event,
        "organization_id": "org-123",
        "data": {
            data_key: {
                id_field: "res-1",
                number_field: "DOC-001",
                "total": 100.0,
                "currency_code": "USD",
                "date": "2026-06-13",
                "status": "open",
                "customer_name": "Test",
            }
        },
    }
    parsed = parse_webhook_event(body)
    assert parsed.event_type == event
    assert parsed.resource_id == "res-1"


def test_parse_invoice_created():
    parsed = parse_webhook_event(_invoice_body())
    assert parsed.event_type == "invoice.created"
    assert parsed.resource_id == "inv-001"
    assert parsed.organization_id == "org-123"


def test_parse_invoice_updated():
    parsed = parse_webhook_event(_invoice_body("invoice.updated"))
    assert parsed.event_type == "invoice.updated"


def test_missing_event_raises():
    with pytest.raises(ValueError, match="Missing Zoho event"):
        parse_webhook_event({"organization_id": "x", "data": {}})


def test_parse_default_zoho_invoice_payload():
    body = {
        "invoice_id": "460000000040001",
        "invoice_number": "INV-000001",
        "customer_name": "John Smith",
        "total": 125.0,
        "currency_code": "USD",
        "status": "sent",
        "date": "2026-06-13",
        "due_date": "2026-07-13",
    }
    parsed = parse_webhook_event(body, default_organization_id="927684356")
    assert parsed.event_type == "invoice.created"
    assert parsed.resource_id == "460000000040001"
    assert parsed.organization_id == "927684356"
    assert parsed.document["invoice_number"] == "INV-000001"
