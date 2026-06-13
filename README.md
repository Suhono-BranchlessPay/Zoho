# BranchlessPay Audit Shield — Zoho Books Collector

Immutable audit trail for Zoho Books invoices, payments, bills, credit notes, and purchase orders.

| Item | Value |
|------|-------|
| Scope | **M1 + M2** webhook/collector · **M3 + M4** verify display mapping |
| Local webhook | `POST http://127.0.0.1:8080/webhook/zoho` |
| BP anchor API | `POST https://branchlesspay.com/api/v1/anchor` |
| GitHub | https://github.com/Suhono-BranchlessPay/Zoho |
| Branch | **`dev` only** |

---

## What this does

1. Zoho Books fires a workflow webhook (`invoice.created`, `payment.created`, etc.).
2. Collector verifies `X-Zoho-Webhook-Token` against `ZOHO_WEBHOOK_TOKEN`.
3. Normalizes webhook payload to BranchlessPay anchor format (`erp: zoho_books`).
4. POSTs to BranchlessPay → verify at `https://branchlesspay.com/verify/[anchor_id]`.
5. **M3+M4:** `display/src/zohoVerifyMapping.ts` for verify page sections.

**Note:** Zoho webhook payloads include amount — no separate enrichment worker required.

---

## Event mapping

| Zoho event | BP `event_type` | Document |
|------------|-----------------|----------|
| `invoice.created` | `zoho_invoice_created` | Invoice |
| `invoice.updated` | `zoho_invoice_updated` | Invoice |
| `payment.created` | `zoho_payment_received` | Payment |
| `bill.created` | `zoho_bill_created` | Bill |
| `creditnote.created` | `zoho_creditnote_created` | Credit Note |
| `purchaseorder.created` | `zoho_po_created` | Purchase Order |

---

## Regional API domains

Set `ZOHO_REGION` in `.env`:

| Region | API base |
|--------|----------|
| US | `books.zoho.com` |
| EU | `books.zoho.eu` |
| IN | `books.zoho.in` |
| AU | `books.zoho.com.au` |
| JP | `books.zoho.jp` |
| CA | `books.zoho.ca` |
| UK | `books.zoho.uk` |
| SA | `books.zoho.sa` |

---

## Quick start

```powershell
cd Zoho
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — BP_LICENSE_KEY, ZOHO_WEBHOOK_TOKEN, ZOHO_ORGANIZATION_ID

$env:PYTHONPATH = "src"
python -m zoho_bp_collector.app
```

Health: http://127.0.0.1:8080/health

---

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```

---

## Project layout

```
Zoho/
├── display/                   # M3+M4 verify-page mapping
├── src/zoho_bp_collector/     # M1+M2 Flask webhook pipeline
├── scripts/
├── tests/
├── docs/
├── MILESTONE_ZOHO.md
└── MILESTONE_M3_M4.md
```

Contact: suhono@branchlesspay.com
