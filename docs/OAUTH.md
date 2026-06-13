# Zoho Books OAuth (optional — for API invoice creation)

1. Open https://api-console.zoho.com/
2. **Add Client** → Server-based Application
3. Redirect URI: `http://localhost:8080/oauth/callback`
4. Scopes: `ZohoBooks.fullaccess.all` (or `ZohoBooks.invoices.CREATE`, `ZohoBooks.contacts.CREATE`)
5. Copy **Client ID** and **Client Secret** to `.env`:

```env
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_ACCESS_TOKEN=
ZOHO_REFRESH_TOKEN=
ZOHO_ORGANIZATION_ID=927684356
ZOHO_REGION=US
```

6. Authorize and exchange code for tokens (same pattern as Xero `scripts/oauth_setup.ps1`).

Then run:

```powershell
python scripts/live_create_test_invoice.py
```

**Note:** Webhook testing does **not** require OAuth — create invoice in Zoho Books UI if OAuth is not set up yet.
