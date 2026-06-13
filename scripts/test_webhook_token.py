"""Live test with ZOHO_WEBHOOK_TOKEN from .env (token verification ON)."""

import json
from dataclasses import replace

from zoho_bp_collector.app import create_app
from zoho_bp_collector.config import get_settings


def main() -> None:
    settings = get_settings()
    settings = replace(settings, skip_token_verify=False)
    app = create_app(settings)
    client = app.test_client()

    payload = {
        "event": "invoice.updated",
        "organization_id": settings.zoho_organization_id or "org-live",
        "data": {
            "invoice": {
                "invoice_id": "live-inv-zoho-002",
                "invoice_number": "INV-ZOHO-002",
                "customer_name": "Jane Doe",
                "total": 750.00,
                "currency_code": "USD",
                "date": "2026-06-13",
                "status": "sent",
            }
        },
    }
    body = json.dumps(payload)

    bad = client.post(
        "/webhook/zoho",
        data=body,
        content_type="application/json",
        headers={"X-Zoho-Webhook-Token": "wrong-token"},
    )
    print("bad_token:", bad.status_code)

    good = client.post(
        "/webhook/zoho",
        data=body,
        content_type="application/json",
        headers={"X-Zoho-Webhook-Token": settings.zoho_webhook_token},
    )
    print("good_token:", good.status_code)
    if good.status_code == 202:
        print(json.dumps(good.get_json(), indent=2))


if __name__ == "__main__":
    main()
