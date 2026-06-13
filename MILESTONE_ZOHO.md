# Milestone — Zoho Books × BranchlessPay (M1 + M2)

Repo: https://github.com/Suhono-BranchlessPay/Zoho  
Branch: **`dev` only**  
Status: **M1–M4 complete** — BP verify mapping merged (`81501e4`)

---

## M1 — Webhook receiver

| Deliverable | Status |
|-------------|--------|
| `POST /webhook/zoho` | ✅ |
| `X-Zoho-Webhook-Token` verification | ✅ |
| Parse Zoho webhook JSON (6 events) | ✅ |
| Multi-region config (`ZOHO_REGION`) | ✅ |
| Dev simulate script | ✅ |
| Docs | ✅ |

---

## M2 — Normalize + BP anchor

| Deliverable | Status |
|-------------|--------|
| Normalizer (amount from webhook payload) | ✅ |
| BP poster + idempotency + failed queue | ✅ |
| 6 event types mapped | ✅ |
| Unit tests (Python) | ✅ |
| Live E2E with Zoho Books trial | ✅ All 6 event types anchored |

---

## M3 + M4 — See [MILESTONE_M3_M4.md](MILESTONE_M3_M4.md)

Contact: suhono@branchlesspay.com
