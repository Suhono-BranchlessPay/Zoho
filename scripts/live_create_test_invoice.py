"""Create a test invoice in Zoho Books (triggers workflow webhook if rule is active)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
load_dotenv(os.path.join(ROOT, ".env"), override=True)

from zoho_bp_collector.zoho_client import ZohoBooksClient  # noqa: E402


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(
            "ERROR: %s is not set in .env\n"
            "Run OAuth first — see docs/OAUTH.md or create invoice manually in Zoho Books UI."
            % name
        )
        sys.exit(1)
    return value


def main() -> int:
    access = _require("ZOHO_ACCESS_TOKEN")
    org_id = _require("ZOHO_ORGANIZATION_ID")
    client_id = os.getenv("ZOHO_CLIENT_ID", "").strip()
    client_secret = os.getenv("ZOHO_CLIENT_SECRET", "").strip()
    refresh = os.getenv("ZOHO_REFRESH_TOKEN", "").strip()
    region = os.getenv("ZOHO_REGION", "US").strip()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    customer_name = os.getenv("ZOHO_TEST_CUSTOMER", "Audit Shield Test Customer")
    line_name = os.getenv("ZOHO_TEST_LINE_ITEM", "BranchlessPay Audit Test")
    rate = float(os.getenv("ZOHO_TEST_AMOUNT", "125"))
    ref = "BP-ZOHO-%s" % stamp

    client = ZohoBooksClient(
        access_token=access,
        organization_id=org_id,
        refresh_token=refresh,
        client_id=client_id,
        client_secret=client_secret,
        region=region,
    )

    print("Organization ID:", org_id)
    print("Creating/finding customer:", customer_name)
    contact = client.get_or_create_customer(customer_name)
    customer_id = str(contact.get("contact_id") or "")
    print("Customer ID:", customer_id)

    print("Creating invoice ref=%s amount=%s" % (ref, rate))
    invoice = client.create_invoice(
        customer_id,
        line_name=line_name,
        rate=rate,
        reference=ref,
    )
    invoice_id = str(invoice.get("invoice_id") or "")
    invoice_number = str(invoice.get("invoice_number") or "")
    print("Invoice created: %s (%s)" % (invoice_number, invoice_id))

    print("Marking invoice as sent (triggers workflow)...")
    sent = client.mark_invoice_sent(invoice_id)
    print("Status:", sent.get("status") if isinstance(sent, dict) else sent)
    print("\nDone. Check collector log for webhook + verify_url.")
    print("Zoho Books URL: https://books.zoho.com/app/%s#/invoices/%s" % (org_id, invoice_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
