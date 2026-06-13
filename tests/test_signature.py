"""Zoho webhook token tests."""

from zoho_bp_collector.signature import get_token_header, verify_webhook_token


def test_verify_webhook_token():
    token = "zoho_secret_token_123"
    assert verify_webhook_token(token, token)
    assert not verify_webhook_token(token, "wrong")
    assert not verify_webhook_token("", token)


def test_get_token_header_case_insensitive():
    headers = {"X-Zoho-Webhook-Token": "abc123"}
    assert get_token_header(headers) == "abc123"
