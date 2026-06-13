# Setup

## Prerequisites

- Python 3.11+
- Node.js 20+ (for display tests)
- Zoho Books trial org
- BranchlessPay test token (`BP_LICENSE_KEY`)

## Environment

```powershell
copy .env.example .env
```

Required variables:

| Variable | Description |
|----------|-------------|
| `BP_LICENSE_KEY` | BranchlessPay test token |
| `ZOHO_WEBHOOK_TOKEN` | From Zoho Books webhook config |
| `ZOHO_ORGANIZATION_ID` | Zoho org ID |
| `ZOHO_ORG_NAME` | Display name on verify page |
| `ZOHO_REGION` | US, EU, IN, AU, JP, CA, UK, or SA |

Optional OAuth (for future API enrichment):

| Variable | Description |
|----------|-------------|
| `ZOHO_CLIENT_ID` | Zoho API console client |
| `ZOHO_CLIENT_SECRET` | Client secret |
| `ZOHO_REFRESH_TOKEN` | OAuth refresh token |

## Run collector

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_server.ps1
```

## Run tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```
