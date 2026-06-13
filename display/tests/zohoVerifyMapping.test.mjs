import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  formatAmountForDisplay,
  formatCurrency,
  getStatusBadge,
  isZohoAnchor,
  mapBusinessSection,
  mapTransactionSection,
  mapZohoVerifyPage,
  shouldShowDueDate,
} from "../src/zohoVerifyMapping.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(__dirname, "..", "fixtures");

const sampleInvoice = JSON.parse(
  readFileSync(join(fixturesDir, "sample-invoice.json"), "utf8"),
);

test("isZohoAnchor detects Zoho records", () => {
  assert.equal(isZohoAnchor(sampleInvoice), true);
  assert.equal(isZohoAnchor({ event_type: "xero_invoice_created" }), false);
});

test("business section maps M3 fields", () => {
  const rows = mapBusinessSection(sampleInvoice);
  assert.equal(rows[0].label, "Business");
  assert.equal(rows[0].value, "Test Company");
  assert.equal(rows[2].value, "Zoho Books");
});

test("status badges for Zoho invoice statuses", () => {
  assert.deepEqual(getStatusBadge("draft"), { label: "Draft", variant: "draft" });
  assert.deepEqual(getStatusBadge("paid"), { label: "Paid", variant: "paid" });
  assert.deepEqual(getStatusBadge("overdue"), {
    label: "Overdue",
    variant: "overdue",
  });
  assert.deepEqual(getStatusBadge("partially_paid"), {
    label: "Partially Paid",
    variant: "partial",
  });
});

test("mapZohoVerifyPage builds full verify output", () => {
  const page = mapZohoVerifyPage(sampleInvoice);
  assert.equal(
    page.transactionRows.find((r) => r.label === "Amount")?.value,
    "$1500.00",
  );
  assert.match(page.instructions, /Zoho Books/);
});

test("payment hides due date", () => {
  const payment = {
    ...sampleInvoice,
    event_type: "zoho_payment_received",
    metadata: { ...sampleInvoice.metadata, due_date: null, status: "paid" },
  };
  assert.equal(shouldShowDueDate(payment), false);
});

test("formatCurrency multi-region", () => {
  assert.equal(formatCurrency(1500, "USD"), "$1500.00");
  assert.equal(formatCurrency(999, "INR"), "₹999.00");
  assert.equal(formatCurrency(500, "AED"), "AED 500.00");
  assert.equal(formatCurrency(250, "EUR"), "€250.00");
  assert.equal(formatCurrency(100, "SGD"), "S$100.00");
});

test("bill event shows vendor label", () => {
  const bill = {
    ...sampleInvoice,
    event_type: "zoho_bill_created",
    reference_id: "BILL-001",
    metadata: {
      ...sampleInvoice.metadata,
      bill_number: "BILL-001",
      contact_name: "Acme Supplies",
      document_type: "Bill",
    },
  };
  const rows = mapTransactionSection(bill);
  assert.equal(rows.find((r) => r.label === "Vendor")?.value, "Acme Supplies");
});

test("credit note reference mapping", () => {
  const cn = {
    ...sampleInvoice,
    event_type: "zoho_creditnote_created",
    reference_id: "CN-001",
    metadata: {
      ...sampleInvoice.metadata,
      creditnote_number: "CN-001",
      document_type: "Credit Note",
    },
  };
  const page = mapZohoVerifyPage(cn);
  assert.equal(
    page.transactionRows.find((r) => r.label === "Reference")?.value,
    "CN-001",
  );
});

test("purchase order hides status row", () => {
  const po = {
    ...sampleInvoice,
    event_type: "zoho_po_created",
    metadata: {
      ...sampleInvoice.metadata,
      purchaseorder_number: "PO-001",
      document_type: "Purchase Order",
      status: "open",
    },
  };
  const rows = mapTransactionSection(po);
  assert.equal(rows.some((r) => r.label === "Status"), false);
});

test("amount displays directly from webhook payload", () => {
  assert.equal(formatAmountForDisplay(sampleInvoice), "$1500.00");
});

test("invoice updated event label", () => {
  const updated = { ...sampleInvoice, event_type: "zoho_invoice_updated" };
  const page = mapZohoVerifyPage(updated);
  assert.equal(
    page.transactionRows.find((r) => r.label === "Document Type")?.value,
    "Zoho Invoice (Updated)",
  );
});
