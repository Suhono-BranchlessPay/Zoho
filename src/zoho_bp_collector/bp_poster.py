"""POST normalized payloads to BranchlessPay API with retry queue."""

import hashlib
import json
import logging
import time
from typing import Any

import requests

from .queue_store import FailedQueue

_logger = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 1.5


def legacy_content_hash(payload: dict[str, Any]) -> str:
    data = {k: v for k, v in payload.items() if k != "content_hash"}
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class BPPoster:
    def __init__(
        self,
        license_key: str,
        api_url: str,
        queue: FailedQueue | None = None,
    ):
        self.license_key = license_key
        self.api_url = api_url.rstrip("/")
        self.queue = queue or FailedQueue()
        self.headers = {
            "Authorization": "Bearer %s" % license_key,
            "Content-Type": "application/json",
        }

    def post_anchor(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.license_key or "YOUR_TOKEN" in self.license_key:
            raise RuntimeError("BP_LICENSE_KEY is not configured")

        body = dict(payload)
        body["content_hash"] = legacy_content_hash(body)
        last_error: str | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    self.api_url,
                    json=body,
                    headers=self.headers,
                    timeout=15,
                )
                if response.status_code in (200, 202):
                    result = response.json()
                    result["ok"] = result.get("ok", True)
                    result["content_hash"] = body["content_hash"]
                    _logger.info(
                        "BP anchor ok anchor_id=%s status=%s",
                        result.get("anchor_id"),
                        result.get("status"),
                    )
                    return result

                last_error = "HTTP %s: %s" % (
                    response.status_code,
                    response.text[:500],
                )
                _logger.error("BP API error: %s", last_error)
            except Exception as exc:
                last_error = str(exc)
                _logger.exception("BP API exception on attempt %s", attempt)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SEC * attempt)

        failure = {
            "ok": False,
            "error": last_error or "unknown",
            "payload": body,
        }
        self.queue.save(body, failure)
        return failure
