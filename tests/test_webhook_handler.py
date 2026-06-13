import json
from unittest.mock import patch

import pytest

from zoho_bp_collector.app import create_app
from zoho_bp_collector.config import Settings


def _settings(**overrides):
    base = dict(
        bp_license_key="bp_test_dummy",
        bp_api_url="https://branchlesspay.com/api/v1/anchor",
        zoho_client_id="cid",
        zoho_client_secret="sec",
        zoho_access_token="access",
        zoho_refresh_token="refresh",
        zoho_organization_id="org-123",
        zoho_org_name="Test Company",
        zoho_org_address="123 Main St",
        zoho_webhook_token="zoho_test_token",
        zoho_region="US",
        host="127.0.0.1",
        port=8080,
        skip_token_verify=True,
        failed_queue_dir="data/failed_queue",
    )
    base.update(overrides)
    return Settings(**base)


def _zoho_webhook_body(event_type: str = "invoice.created"):
    data_key_map = {
        "invoice.created": "invoice",
        "invoice.updated": "invoice",
        "payment.created": "payment",
        "bill.created": "bill",
        "creditnote.created": "creditnote",
        "purchaseorder.created": "purchaseorder",
    }
    doc_map = {
        "invoice.created": {
            "invoice_id": "inv-1",
            "invoice_number": "INV-0001",
            "customer_name": "John Smith",
            "total": 750.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "due_date": "2026-07-12",
            "status": "draft",
        },
        "invoice.updated": {
            "invoice_id": "inv-1",
            "invoice_number": "INV-0001",
            "customer_name": "John Smith",
            "total": 750.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "status": "sent",
        },
        "payment.created": {
            "payment_id": "pay-1",
            "reference_number": "PAY-001",
            "amount": 100.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "customer_name": "Jane Doe",
            "status": "paid",
        },
        "bill.created": {
            "bill_id": "bill-1",
            "bill_number": "BILL-001",
            "vendor_name": "Acme",
            "total": 200.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "status": "open",
        },
        "creditnote.created": {
            "creditnote_id": "cn-1",
            "creditnote_number": "CN-001",
            "customer_name": "John Smith",
            "total": 50.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "status": "open",
        },
        "purchaseorder.created": {
            "purchaseorder_id": "po-1",
            "purchaseorder_number": "PO-001",
            "vendor_name": "Supplier Co",
            "total": 300.0,
            "currency_code": "USD",
            "date": "2026-06-12",
            "status": "open",
        },
    }
    key = data_key_map[event_type]
    return {
        "event": event_type,
        "organization_id": "org-123",
        "data": {key: doc_map[event_type]},
    }


@pytest.mark.parametrize(
    "event_type",
    [
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "bill.created",
        "creditnote.created",
        "purchaseorder.created",
    ],
)
@patch("zoho_bp_collector.app.AnchorIdempotencyStore")
@patch("zoho_bp_collector.app.BPPoster.post_anchor")
def test_webhook_pipeline_all_events(mock_post, mock_idem_cls, event_type):
    mock_idem_cls.return_value.get.return_value = None
    mock_post.return_value = {
        "ok": True,
        "anchor_id": "test-anchor-%s" % event_type.replace(".", "-"),
        "status": "queued",
    }

    app = create_app(_settings())
    client = app.test_client()
    payload = _zoho_webhook_body(event_type)
    response = client.post(
        "/webhook/zoho",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 202
    body = response.get_json()
    assert body["ok"] is True
    assert body["anchor_id"]


def test_invalid_token_returns_401():
    app = create_app(_settings(skip_token_verify=False))
    client = app.test_client()
    payload = _zoho_webhook_body()
    response = client.post(
        "/webhook/zoho",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-Zoho-Webhook-Token": "wrong"},
    )
    assert response.status_code == 401


def test_valid_token_returns_202():
    app = create_app(_settings(skip_token_verify=False))
    client = app.test_client()
    payload = _zoho_webhook_body()
    with patch("zoho_bp_collector.app.AnchorIdempotencyStore") as mock_idem_cls, patch(
        "zoho_bp_collector.app.BPPoster.post_anchor"
    ) as mock_post:
        mock_idem_cls.return_value.get.return_value = None
        mock_post.return_value = {
            "ok": True,
            "anchor_id": "anchor-token-test",
            "status": "queued",
        }
        response = client.post(
            "/webhook/zoho",
            data=json.dumps(payload),
            content_type="application/json",
            headers={"X-Zoho-Webhook-Token": "zoho_test_token"},
        )
    assert response.status_code == 202
