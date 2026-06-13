# M3 Field Mapping — Zoho Books

Source: `display/src/zohoVerifyMapping.ts`

## Business Information

| Verify label | Source |
|--------------|--------|
| Business | `metadata.business_name` |
| Address | `metadata.business_address` |
| ERP System | `"Zoho Books"` |

## Transaction Details

| Verify label | Source |
|--------------|--------|
| Reference | `metadata.invoice_number` / bill / credit note / PO number |
| Document Type | Event type label |
| Contact / Vendor | `metadata.contact_name` |
| Date | `voucher_date` or `metadata.create_date` |
| Due Date | `metadata.due_date` (hidden if null) |
| Amount | `amount` + `currency_code` |
| Status | `metadata.status` badge |

## Event labels

| BP `event_type` | Label |
|-----------------|-------|
| `zoho_invoice_created` | Zoho Invoice |
| `zoho_invoice_updated` | Zoho Invoice (Updated) |
| `zoho_payment_received` | Zoho Payment |
| `zoho_bill_created` | Zoho Bill |
| `zoho_creditnote_created` | Zoho Credit Note |
| `zoho_po_created` | Zoho Purchase Order |

## Status badges

| Zoho status | Badge |
|-------------|-------|
| draft | grey |
| sent | blue |
| paid | green |
| overdue | red |
| void | red |
| partially_paid | yellow |

## Multi-currency

USD `$`, INR `₹`, AED `AED`, EUR `€`, GBP `£`, AUD `A$`, SGD `S$`, CAD `CA$`
