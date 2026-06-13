"""One-shot live BP anchor test — run with BP_LICENSE_KEY in .env."""

import json
from unittest.mock import patch

from zoho_bp_collector.app import create_app
from zoho_bp_collector.config import get_settings

app = create_app(get_settings())
client = app.test_client()
payload = {
    "event": "invoice.created",
    "organization_id": "org-test-live-001",
    "data": {
        "invoice": {
            "invoice_id": "live-inv-zoho-001",
            "invoice_number": "INV-ZOHO-001",
            "customer_name": "John Smith",
            "total": 1500.00,
            "currency_code": "USD",
            "date": "2026-06-13",
            "due_date": "2026-07-13",
            "status": "draft",
        }
    },
}

with patch("zoho_bp_collector.app.AnchorIdempotencyStore") as mock_idem:
    mock_idem.return_value.get.return_value = None
    resp = client.post(
        "/webhook/zoho",
        data=json.dumps(payload),
        content_type="application/json",
    )
    print(resp.status_code)
    print(json.dumps(resp.get_json(), indent=2))
