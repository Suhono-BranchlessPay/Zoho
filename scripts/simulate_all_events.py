"""Simulate all 6 Zoho Books webhook event types and collect verify URLs."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"), override=True)

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
WEBHOOK_URL = "%s/webhook/zoho" % BASE_URL.rstrip("/")


def _suffix() -> str:
    return uuid.uuid4().hex[:6].upper()


def _build_events() -> list[tuple[str, dict, str | None]]:
    s = _suffix()
    org = os.getenv("ZOHO_ORGANIZATION_ID", "927684356")
    customer = "Audit Shield Test Customer"
    vendor = "Acme Supplies Co"

    return [
        (
            "invoice.updated",
            {
                "event": "invoice.updated",
                "organization_id": org,
                "invoice_id": "460000000040010",
                "invoice_number": "INV-UPD-%s" % s,
                "customer_name": customer,
                "total": 500.0,
                "currency_code": "USD",
                "status": "sent",
                "date": "2026-06-13",
                "due_date": "2026-07-13",
            },
            None,
        ),
        (
            "payment.created",
            {
                "payment_id": "460000000050001",
                "reference_number": "PAY-%s" % s,
                "amount": 250.0,
                "customer_name": customer,
                "currency_code": "USD",
                "date": "2026-06-13",
                "status": "paid",
            },
            None,
        ),
        (
            "bill.created",
            {
                "bill_id": "460000000060001",
                "bill_number": "BILL-%s" % s,
                "vendor_name": vendor,
                "total": 180.0,
                "currency_code": "USD",
                "date": "2026-06-13",
                "due_date": "2026-07-13",
                "status": "open",
            },
            None,
        ),
        (
            "creditnote.created",
            {
                "creditnote_id": "460000000070001",
                "creditnote_number": "CN-%s" % s,
                "customer_name": customer,
                "total": 75.0,
                "currency_code": "AED",
                "date": "2026-06-13",
                "status": "open",
            },
            None,
        ),
        (
            "purchaseorder.created",
            {
                "purchaseorder_id": "460000000080001",
                "purchaseorder_number": "PO-%s" % s,
                "vendor_name": vendor,
                "total": 920.0,
                "currency_code": "USD",
                "date": "2026-06-13",
                "status": "open",
            },
            None,
        ),
    ]


def main() -> int:
    token = os.getenv("ZOHO_WEBHOOK_TOKEN", "").strip()
    bp_key = os.getenv("BP_LICENSE_KEY", "").strip()
    if not token:
        print("ERROR: ZOHO_WEBHOOK_TOKEN not set")
        return 1

    headers = {
        "Content-Type": "application/json",
        "X-Zoho-Webhook-Token": token,
    }

    results = []
    for event_type, payload, _ in _build_events():
        t0 = time.time()
        response = requests.post(
            WEBHOOK_URL, json=payload, headers=headers, timeout=30
        )
        ms = int((time.time() - t0) * 1000)
        entry = {
            "event_type": event_type,
            "http_status": response.status_code,
            "ms": ms,
            "reference": payload.get("invoice_number")
            or payload.get("reference_number")
            or payload.get("bill_number")
            or payload.get("creditnote_number")
            or payload.get("purchaseorder_number"),
        }
        try:
            body = response.json()
            entry.update(
                {
                    "ok": body.get("ok"),
                    "anchor_id": body.get("anchor_id"),
                    "verify_url": body.get("verify_url"),
                    "error": body.get("error"),
                }
            )
        except Exception:
            entry["error"] = response.text[:200]

        if entry.get("anchor_id") and bp_key:
            for _ in range(15):
                verify = requests.get(
                    "https://branchlesspay.com/api/v1/verify/%s"
                    % entry["anchor_id"],
                    headers={"Authorization": "Bearer %s" % bp_key},
                    timeout=15,
                )
                if verify.json().get("status") == "anchored":
                    entry["bp_status"] = "anchored"
                    break
                time.sleep(2)
            else:
                entry["bp_status"] = verify.json().get("status", "unknown")

        results.append(entry)
        print(json.dumps(entry, indent=2))

    out_path = os.path.join(ROOT, "docs", "LIVE_VERIFY_URLS.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print("\nSaved:", out_path)
    return 0 if all(r.get("http_status") == 202 for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
