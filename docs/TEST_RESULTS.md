# Test Results — Zoho Books

Date: 2026-06-13

## Python (pytest)

```
25 passed
```

Covers: token verification, webhook parser (6 events), normalizer, full pipeline mocks.

## Display (node:test)

```
11 passed
```

Covers: M3 field mapping, status badges, multi-currency, M4 polish.

## Live BP anchor

Attempted `scripts/live_anchor_test.py` — pipeline normalizes correctly; BP returned `401 Invalid API key` (needs valid `BP_LICENSE_KEY` from Bos via WhatsApp).

## Next

1. Configure Zoho Books webhook → cloudflared → local collector
2. Valid `BP_LICENSE_KEY` for live anchor + verify URL
3. BP team: merge `zohoVerifyMapping.ts` into VerifyPage (like Xero `db11427`)
