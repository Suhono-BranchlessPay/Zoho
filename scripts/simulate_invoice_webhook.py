"""Simulate Zoho Books invoice.created webhook via tunnel or localhost."""

import json
import os
import sys
import uuid

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)


def main() -> None:
    token = os.getenv("ZOHO_WEBHOOK_TOKEN", "").strip()
    org_id = os.getenv("ZOHO_ORGANIZATION_ID", "927684356").strip()
    org_name = os.getenv("ZOHO_ORG_NAME", "Zoho Organisation").strip()
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    url = "%s/webhook/zoho" % base_url.rstrip("/")

    suffix = uuid.uuid4().hex[:6].upper()
    invoice_number = "INV-TEST-%s" % suffix
    invoice_id = "zoho-inv-%s" % uuid.uuid4().hex[:12]

    payload = {
        "event": "invoice.created",
        "organization_id": org_id,
        "data": {
            "invoice": {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "customer_name": "Audit Shield Test Customer",
                "total": 1250.00,
                "currency_code": "USD",
                "date": "2026-06-13",
                "due_date": "2026-07-13",
                "status": "sent",
                "company_name": org_name,
            }
        },
    }

    headers = {
        "Content-Type": "application/json",
        "X-Zoho-Webhook-Token": token,
    }

    print("POST", url)
    print("invoice_number", invoice_number)
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print("status", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text[:500])


if __name__ == "__main__":
    main()
