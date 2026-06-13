/**
 * Zoho Books verify-page field mapping for BranchlessPay VerifyPage.tsx.
 */

export type ZohoStatus =
  | "draft"
  | "sent"
  | "paid"
  | "overdue"
  | "void"
  | "partially_paid"
  | string;

export type StatusBadgeVariant =
  | "unpaid"
  | "paid"
  | "overdue"
  | "draft"
  | "partial"
  | "saved"
  | "sent"
  | "unknown";

export interface ZohoAnchorMetadata {
  erp?: string;
  erp_system?: string;
  company_name?: string | null;
  business_name?: string | null;
  business_address?: string | null;
  organization_id?: string | null;
  document_type?: string | null;
  contact_name?: string | null;
  invoice_number?: string | null;
  bill_number?: string | null;
  creditnote_number?: string | null;
  purchaseorder_number?: string | null;
  status?: ZohoStatus | null;
  due_date?: string | null;
  voucher_date?: string | null;
  create_date?: string | null;
  payment_date?: string | null;
  zoho_event?: string | null;
  zoho_id?: string | null;
  currency_code?: string | null;
  region?: string | null;
  amount_enriched?: boolean | null;
}

export interface ZohoAnchorRecord {
  event_type?: string;
  reference_id?: string;
  amount?: number;
  currency?: string;
  voucher_date?: string;
  timestamp?: string;
  organization_id?: string;
  business_name?: string;
  business_address?: string;
  erp_system?: string;
  metadata?: ZohoAnchorMetadata;
}

export interface VerifyRow {
  label: string;
  value: string;
  hidden?: boolean;
}

export interface StatusBadge {
  label: string;
  variant: StatusBadgeVariant;
}

export interface PdfEvidenceFields {
  documentNumber: string;
  clientName: string;
  dueDate: string | null;
  documentType: string;
  amountFormatted: string;
  currency: string;
}

export interface ZohoVerifyPageData {
  businessRows: VerifyRow[];
  transactionRows: VerifyRow[];
  statusBadge: StatusBadge;
  instructions: string;
  pdfFields: PdfEvidenceFields;
}

export const ERP_DISPLAY_LABEL = "Zoho Books";

export const EVENT_TYPE_LABELS: Record<string, string> = {
  zoho_invoice_created: "Zoho Invoice",
  zoho_invoice_updated: "Zoho Invoice (Updated)",
  zoho_payment_received: "Zoho Payment",
  zoho_bill_created: "Zoho Bill",
  zoho_creditnote_created: "Zoho Credit Note",
  zoho_po_created: "Zoho Purchase Order",
};

export const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  sent: "Sent",
  paid: "Paid",
  overdue: "Overdue",
  void: "Void",
  partially_paid: "Partially Paid",
};

export const STATUS_BADGE_VARIANTS: Record<string, StatusBadgeVariant> = {
  draft: "draft",
  sent: "sent",
  paid: "paid",
  overdue: "overdue",
  void: "unknown",
  partially_paid: "partial",
};

const INVOICE_EVENT_TYPES = new Set([
  "zoho_invoice_created",
  "zoho_invoice_updated",
]);

const BILL_EVENT_TYPES = new Set(["zoho_bill_created"]);

const SUPPORTED_CURRENCIES = new Set([
  "USD",
  "CAD",
  "AUD",
  "NZD",
  "GBP",
  "INR",
  "AED",
  "EUR",
  "SGD",
]);

export function isZohoAnchor(anchor: ZohoAnchorRecord): boolean {
  const erp = anchor.metadata?.erp?.toLowerCase();
  const vendor = (anchor.metadata as { vendor?: string } | undefined)?.vendor?.toLowerCase();
  const eventType = anchor.event_type ?? "";
  return (
    erp === "zoho_books" ||
    erp === "zoho" ||
    vendor === "zoho" ||
    eventType.startsWith("zoho_")
  );
}

export function displayOrDash(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }
  const trimmed = String(value).trim();
  return trimmed === "" ? "-" : trimmed;
}

export function formatCurrency(amount: number, currency = "USD"): string {
  const code = (currency || "USD").toUpperCase();
  const safeAmount = Number.isFinite(amount) ? amount : 0;
  const fixed = safeAmount.toFixed(2);

  switch (code) {
    case "USD":
      return `$${fixed}`;
    case "CAD":
      return `CA$${fixed}`;
    case "AUD":
      return `A$${fixed}`;
    case "NZD":
      return `NZ$${fixed}`;
    case "GBP":
      return `£${fixed}`;
    case "INR":
      return `₹${fixed}`;
    case "AED":
      return `AED ${fixed}`;
    case "EUR":
      return `€${fixed}`;
    case "SGD":
      return `S$${fixed}`;
    default:
      return `${code} ${fixed}`;
  }
}

/** Zoho webhook payloads include amount — no enrichment worker needed. */
export function formatAmountForDisplay(anchor: ZohoAnchorRecord): string {
  const amount = anchor.amount ?? 0;
  const currency =
    anchor.currency ?? anchor.metadata?.currency_code ?? "USD";
  return formatCurrency(amount, currency);
}

export function formatDisplayDate(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const dateOnly = value.split("T")[0].split(" ")[0];
  const parsed = new Date(`${dateOnly}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

export function getEventTypeLabel(eventType: string | undefined): string {
  if (!eventType) {
    return ERP_DISPLAY_LABEL;
  }
  return EVENT_TYPE_LABELS[eventType] ?? eventType;
}

export function isInvoiceEvent(anchor: ZohoAnchorRecord): boolean {
  return INVOICE_EVENT_TYPES.has(anchor.event_type ?? "");
}

export function isBillEvent(anchor: ZohoAnchorRecord): boolean {
  return BILL_EVENT_TYPES.has(anchor.event_type ?? "");
}

export function getStatusBadge(status: ZohoStatus | null | undefined): StatusBadge {
  const normalized = String(status ?? "unknown").toLowerCase();
  const label = STATUS_LABELS[normalized] ?? displayOrDash(status ?? undefined);
  const variant = STATUS_BADGE_VARIANTS[normalized] ?? "unknown";
  return { label, variant };
}

export function getBusinessName(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(
    metadata.business_name ?? metadata.company_name ?? anchor.business_name,
  );
}

export function getBusinessAddress(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(metadata.business_address ?? anchor.business_address);
}

export function getReferenceId(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const eventType = anchor.event_type ?? "";

  if (eventType === "zoho_creditnote_created" && metadata.creditnote_number) {
    return displayOrDash(metadata.creditnote_number);
  }
  if (eventType === "zoho_po_created" && metadata.purchaseorder_number) {
    return displayOrDash(metadata.purchaseorder_number);
  }
  if (eventType === "zoho_bill_created" && metadata.bill_number) {
    return displayOrDash(metadata.bill_number);
  }
  if (metadata.invoice_number) {
    return displayOrDash(metadata.invoice_number);
  }
  if (metadata.bill_number) {
    return displayOrDash(metadata.bill_number);
  }
  if (metadata.creditnote_number) {
    return displayOrDash(metadata.creditnote_number);
  }
  if (metadata.purchaseorder_number) {
    return displayOrDash(metadata.purchaseorder_number);
  }
  return displayOrDash(anchor.reference_id);
}

export function getTransactionDate(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const eventType = anchor.event_type ?? "";

  let raw: string | undefined;
  if (eventType === "zoho_payment_received") {
    raw = metadata.payment_date ?? anchor.voucher_date ?? metadata.voucher_date;
  } else {
    raw = anchor.voucher_date ?? metadata.voucher_date ?? metadata.create_date ?? anchor.timestamp;
  }

  return formatDisplayDate(raw);
}

export function shouldShowDueDate(anchor: ZohoAnchorRecord): boolean {
  if (!isInvoiceEvent(anchor) && !isBillEvent(anchor)) {
    return false;
  }
  const dueDate = anchor.metadata?.due_date;
  return Boolean(dueDate && String(dueDate).trim() !== "");
}

export function shouldShowStatus(anchor: ZohoAnchorRecord): boolean {
  const status = anchor.metadata?.status;
  if (!status || String(status).trim() === "") {
    return false;
  }
  if (anchor.event_type === "zoho_po_created") {
    return false;
  }
  return true;
}

export function getPartyLabel(anchor: ZohoAnchorRecord): string {
  if (anchor.event_type === "zoho_bill_created") {
    return "Vendor";
  }
  if (anchor.event_type === "zoho_po_created") {
    return "Vendor";
  }
  return "Contact";
}

export function getPartyValue(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(metadata.contact_name);
}

export function mapBusinessSection(anchor: ZohoAnchorRecord): VerifyRow[] {
  return [
    { label: "Business", value: getBusinessName(anchor) },
    { label: "Address", value: getBusinessAddress(anchor) },
    { label: "ERP System", value: ERP_DISPLAY_LABEL },
  ];
}

export function mapTransactionSection(anchor: ZohoAnchorRecord): VerifyRow[] {
  const metadata = anchor.metadata ?? {};
  const rows: VerifyRow[] = [
    { label: "Reference", value: getReferenceId(anchor) },
    {
      label: "Document Type",
      value: displayOrDash(
        getEventTypeLabel(anchor.event_type) ?? metadata.document_type ?? undefined,
      ),
    },
    { label: getPartyLabel(anchor), value: getPartyValue(anchor) },
    { label: "Date", value: getTransactionDate(anchor) },
  ];

  if (shouldShowDueDate(anchor)) {
    rows.push({
      label: "Due Date",
      value: formatDisplayDate(metadata.due_date),
    });
  }

  rows.push({
    label: "Amount",
    value: formatAmountForDisplay(anchor),
  });

  if (shouldShowStatus(anchor)) {
    const badge = getStatusBadge(metadata.status);
    rows.push({ label: "Status", value: badge.label });
  }

  return rows;
}

export function buildVerificationInstructions(anchor: ZohoAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const documentType = metadata.document_type ?? "document";
  const timestamp = formatDisplayDate(anchor.timestamp);
  const orgId = displayOrDash(
    metadata.organization_id ?? anchor.organization_id,
  );
  const eventLabel = getEventTypeLabel(anchor.event_type);
  const region = metadata.region ? ` (${metadata.region})` : "";

  return (
    `This ${eventLabel} (${documentType}) from Zoho Books was anchored to the Monad blockchain on ${timestamp}. ` +
    `Original record in Zoho organisation ${orgId}${region}. Verify the content hash and transaction hash below.`
  );
}

export function buildPdfEvidenceFields(anchor: ZohoAnchorRecord): PdfEvidenceFields {
  const metadata = anchor.metadata ?? {};
  const currency = (
    anchor.currency ??
    metadata.currency_code ??
    "USD"
  ).toUpperCase();
  const safeCurrency = SUPPORTED_CURRENCIES.has(currency) ? currency : "USD";

  return {
    documentNumber: getReferenceId(anchor),
    clientName: getPartyValue(anchor),
    dueDate: shouldShowDueDate(anchor)
      ? formatDisplayDate(metadata.due_date)
      : null,
    documentType: displayOrDash(
      metadata.document_type ?? getEventTypeLabel(anchor.event_type),
    ),
    amountFormatted: formatAmountForDisplay(anchor),
    currency: safeCurrency,
  };
}

export function mapZohoVerifyPage(anchor: ZohoAnchorRecord): ZohoVerifyPageData {
  return {
    businessRows: mapBusinessSection(anchor),
    transactionRows: mapTransactionSection(anchor),
    statusBadge: getStatusBadge(anchor.metadata?.status),
    instructions: buildVerificationInstructions(anchor),
    pdfFields: buildPdfEvidenceFields(anchor),
  };
}
