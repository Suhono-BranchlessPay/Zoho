"""Zoho Books webhook token verification (X-Zoho-Webhook-Token header)."""

import hmac
from typing import Mapping


def verify_webhook_token(
    expected_token: str,
    token_header: str | None,
) -> bool:
    if not expected_token or not token_header:
        return False
    return hmac.compare_digest(
        expected_token.strip(),
        token_header.strip(),
    )


def get_token_header(headers: Mapping[str, str]) -> str | None:
    for key, value in headers.items():
        if key.lower() == "x-zoho-webhook-token":
            return value
    return None
