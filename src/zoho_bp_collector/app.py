"""Flask webhook receiver — M1 + M2 pipeline for Zoho Books."""

import json
import logging
from typing import Any

from flask import Flask, Request, jsonify, request

from .bp_poster import BPPoster
from .config import get_settings
from .idempotency import AnchorIdempotencyStore
from .normalizer import normalize_to_bp_payload
from .queue_store import FailedQueue
from .signature import get_token_header, verify_webhook_token
from .webhook_parser import ANCHOR_EVENTS, parse_webhook_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_logger = logging.getLogger(__name__)


def create_app(settings=None) -> Flask:
    settings = settings or get_settings()
    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "zoho-bp-collector"}), 200

    @app.get("/webhook/zoho")
    @app.post("/webhook/zoho")
    def zoho_webhook():
        if request.method == "GET":
            return jsonify({"ok": True, "verification": "ping"}), 200
        return _handle_webhook(request, settings)

    return app


def _handle_webhook(req: Request, settings) -> tuple[Any, int]:
    raw_body = req.get_data(cache=True)

    try:
        body = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        _logger.warning("Webhook received invalid JSON")
        return jsonify({"ok": False, "error": "invalid json"}), 400

    if not settings.skip_token_verify and settings.zoho_webhook_token:
        token_header = get_token_header(req.headers)
        if not verify_webhook_token(settings.zoho_webhook_token, token_header):
            _logger.warning("Invalid Zoho webhook token")
            return jsonify({"ok": False, "error": "unauthorized"}), 401
    elif settings.skip_token_verify:
        _logger.warning("Token verification skipped (dev mode)")

    try:
        event = parse_webhook_event(body)
    except ValueError as exc:
        _logger.warning("Webhook parse error: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 400

    result, status = _process_event(event, settings)
    return jsonify(result), status


def _process_event(event, settings) -> tuple[dict[str, Any], int]:
    _logger.info(
        "Webhook received event=%s resource_id=%s organization_id=%s",
        event.event_type,
        event.resource_id,
        event.organization_id,
    )

    if event.event_type not in ANCHOR_EVENTS:
        return {"ok": True, "ignored": event.event_type}, 200

    idempotency = AnchorIdempotencyStore()
    idem_key = AnchorIdempotencyStore.make_key(
        event.organization_id, event.event_type, event.resource_id
    )
    cached = idempotency.get(idem_key)
    if cached:
        return cached, 202

    org_name = settings.zoho_org_name
    org_address = settings.zoho_org_address

    try:
        bp_payload = normalize_to_bp_payload(
            event.event_type,
            event.document,
            organization_id=event.organization_id,
            org_name=org_name,
            org_address=org_address,
            region=settings.zoho_region,
        )
    except (TypeError, ValueError) as exc:
        _logger.exception("Normalize failed: %s", exc)
        return {"ok": False, "error": "normalize failed", "detail": str(exc)}, 422

    poster = BPPoster(
        license_key=settings.bp_license_key,
        api_url=settings.bp_api_url,
        queue=FailedQueue(settings.failed_queue_dir),
    )

    try:
        result = poster.post_anchor(bp_payload)
    except Exception as exc:
        _logger.exception("BP post failed: %s", exc)
        return {"ok": False, "error": str(exc)}, 502

    if not result.get("ok"):
        return result, 502

    anchor_id = result.get("anchor_id")
    response = {
        "ok": True,
        "event_type": event.event_type,
        "reference_id": bp_payload["reference_id"],
        "anchor_id": anchor_id,
        "verify_url": "https://branchlesspay.com/verify/%s" % anchor_id if anchor_id else None,
        "status": result.get("status"),
        "idempotent": False,
    }
    idempotency.save(idem_key, {**response, "idempotent": True})
    _logger.info("Pipeline complete verify_url=%s", response.get("verify_url"))
    return response, 202


if __name__ == "__main__":
    cfg = get_settings()
    create_app(cfg).run(host=cfg.host, port=cfg.port, debug=False)
