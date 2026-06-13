"""Zoho normalizer tests."""

import pytest

from zoho_bp_collector.normalizer import map_event_type, normalize_to_bp_payload


SAMPLE_INVOICE = {
    "invoice_id": "inv-001",
    "invoice_number": "INV-000001",
    "customer_name": "John Smith",
    "total": 1500.0,
    "currency_code": "USD",
    "date": "2026-06-13",
    "due_date": "2026-07-13",
    "status": "draft",
}


@pytest.mark.parametrize(
    "zoho_event,bp_event",
    [
        ("invoice.created", "zoho_invoice_created"),
        ("invoice.updated", "zoho_invoice_updated"),
        ("payment.created", "zoho_payment_received"),
        ("bill.created", "zoho_bill_created"),
        ("creditnote.created", "zoho_creditnote_created"),
        ("purchaseorder.created", "zoho_po_created"),
    ],
)
def test_event_type_mapping(zoho_event, bp_event):
    assert map_event_type(zoho_event) == bp_event


def test_normalize_invoice_payload():
    payload = normalize_to_bp_payload(
        "invoice.created",
        SAMPLE_INVOICE,
        organization_id="org-123",
        org_name="Test Company",
        org_address="123 Main St",
        region="US",
    )
    assert payload["event_type"] == "zoho_invoice_created"
    assert payload["reference_id"] == "INV-000001"
    assert payload["amount"] == 1500.0
    assert payload["currency"] == "USD"
    assert payload["metadata"]["erp"] == "zoho_books"
    assert payload["metadata"]["amount_enriched"] is True
    assert payload["metadata"]["region"] == "US"


def test_normalize_payment_payload():
    payment = {
        "payment_id": "pay-1",
        "reference_number": "PAY-001",
        "amount": 500.0,
        "currency_code": "INR",
        "date": "2026-06-13",
        "customer_name": "Jane Doe",
        "status": "paid",
    }
    payload = normalize_to_bp_payload(
        "payment.created",
        payment,
        organization_id="org-in",
        org_name="India Co",
        region="IN",
    )
    assert payload["event_type"] == "zoho_payment_received"
    assert payload["amount"] == 500.0
    assert payload["currency"] == "INR"
