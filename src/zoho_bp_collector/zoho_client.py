"""Zoho Books REST API client with OAuth refresh."""

import logging
import time
from typing import Any

import requests

from .config import ZOHO_API_BASES, ZOHO_TOKEN_URLS

_logger = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 1.5


class ZohoBooksClient:
    def __init__(
        self,
        access_token: str,
        organization_id: str,
        *,
        refresh_token: str = "",
        client_id: str = "",
        client_secret: str = "",
        region: str = "US",
    ):
        self.access_token = access_token
        self.organization_id = organization_id
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.region = region.upper()
        self.api_base = ZOHO_API_BASES.get(self.region, ZOHO_API_BASES["US"])
        self.token_url = ZOHO_TOKEN_URLS.get(self.region, ZOHO_TOKEN_URLS["US"])

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": "Zoho-oauthtoken %s" % self.access_token,
            "Content-Type": "application/json",
        }

    def refresh_access_token(self) -> None:
        if not all([self.refresh_token, self.client_id, self.client_secret]):
            raise RuntimeError("OAuth refresh credentials not configured")
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        _logger.info("Zoho access token refreshed")

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        url = "%s/%s" % (self.api_base, path.lstrip("/"))
        params = dict(kwargs.pop("params", {}) or {})
        params.setdefault("organization_id", self.organization_id)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._headers,
                    params=params,
                    timeout=20,
                    **kwargs,
                )
                if response.status_code == 401 and attempt == 1:
                    self.refresh_access_token()
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                _logger.warning(
                    "Zoho API attempt %s/%s failed: %s", attempt, MAX_RETRIES, exc
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC * attempt)

        raise RuntimeError(
            "Zoho API failed after %s retries: %s" % (MAX_RETRIES, last_error)
        )

    def list_contacts(self, *, contact_type: str = "customer") -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            "contacts",
            params={"contact_type": contact_type},
        )
        return payload.get("contacts") or []

    def create_contact(self, name: str) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "contacts",
            json={"contact_name": name, "contact_type": "customer"},
        )
        contact = payload.get("contact")
        if not contact:
            raise RuntimeError("Zoho did not return contact")
        return contact

    def get_or_create_customer(self, name: str) -> dict[str, Any]:
        for contact in self.list_contacts(contact_type="customer"):
            if str(contact.get("contact_name") or "").strip().lower() == name.lower():
                return contact
        return self.create_contact(name)

    def create_invoice(
        self,
        customer_id: str,
        *,
        line_name: str,
        rate: float,
        quantity: int = 1,
        reference: str = "",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "customer_id": customer_id,
            "line_items": [
                {
                    "name": line_name,
                    "rate": rate,
                    "quantity": quantity,
                }
            ],
        }
        if reference:
            body["reference_number"] = reference

        payload = self._request("POST", "invoices", json=body)
        invoice = payload.get("invoice")
        if not invoice:
            raise RuntimeError("Zoho did not return invoice")
        return invoice

    def mark_invoice_sent(self, invoice_id: str) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "invoices/%s/status/sent" % invoice_id,
        )
        return payload.get("invoice") or payload
