# Zoho Books Webhook Setup

## Endpoint

| Environment | URL |
|-------------|-----|
| Local dev | `http://127.0.0.1:8080/webhook/zoho` |
| Production (BP) | `https://branchlesspay.com/api/v1/webhook/zoho` (pending BP deploy) |

Use **cloudflared** or ngrok to expose local endpoint for Zoho testing.

---

## Configure in Zoho Books

1. Open **Settings → Automation → Webhooks → New Webhook**.
2. Set URL to your public webhook endpoint.
3. Choose events:
   - Invoice Created / Updated
   - Payment Created
   - Bill Created
   - Credit Note Created
   - Purchase Order Created
4. Copy the **webhook token** into `.env`:

```env
ZOHO_WEBHOOK_TOKEN=your_token_here
ZOHO_SKIP_TOKEN_VERIFY=0
```

5. Zoho sends header: `X-Zoho-Webhook-Token: [token]`

---

## Payload format

```json
{
  "event": "invoice.created",
  "data": {
    "invoice": {
      "invoice_id": "xxx",
      "invoice_number": "INV-000001",
      "customer_name": "John Smith",
      "total": 1500.00,
      "currency_code": "USD",
      "date": "2026-06-13",
      "due_date": "2026-07-13",
      "status": "draft"
    }
  },
  "organization_id": "xxx"
}
```

---

## Test locally

```powershell
powershell -ExecutionPolicy Bypass -File scripts\simulate_webhook.ps1
```

Expected: HTTP **202** with `anchor_id` and `verify_url`.

---

## Resources

- [Zoho Books API v3](https://www.zoho.com/books/api/v3/)
- [Zoho Webhooks](https://www.zoho.com/books/api/v3/webhooks/)
