"""Webhook validation and parsing helpers for Exact Online webhooks.

This module provides utilities for processing webhook payloads from Exact Online.
Users host their own webhook endpoint (e.g., in FastAPI, Flask); this module
helps validate and parse incoming webhook data.

Example:
    ```python
    from fastapi import FastAPI, Request, HTTPException
    from exact_online.webhooks import validate_and_parse, WebhookValidationError

    app = FastAPI()

    @app.post("/webhooks/exact")
    async def handle_webhook(request: Request):
        try:
            event = validate_and_parse(
                payload=await request.body(),
                signature=request.headers.get("X-Exact-Signature", ""),
                secret=os.environ["EXACT_WEBHOOK_SECRET"],
            )
        except WebhookValidationError as e:
            raise HTTPException(status_code=401, detail=str(e))

        print(f"Received {event.action} on {event.topic}: {event.key}")
        # Process the webhook event...
        return {"status": "ok"}
    ```
"""

import contextlib
import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger("exact_online.webhooks")


class WebhookValidationError(Exception):
    """Raised when webhook signature validation fails."""


@dataclass
class WebhookEvent:
    """Parsed and validated webhook event.

    Attributes:
        topic: The entity type (e.g., "PurchaseOrders", "Accounts", "Items").
        action: The action performed ("Create", "Update", "Delete").
        division: The division ID where the change occurred.
        key: The GUID of the affected entity.
        endpoint: The API endpoint to fetch the full entity.
        timestamp: When the webhook was sent (if available).
        raw_payload: The original parsed payload data.
    """

    topic: str
    action: str
    division: int
    key: str
    endpoint: str
    timestamp: datetime | None = None
    raw_payload: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return (
            f"WebhookEvent(topic={self.topic!r}, action={self.action!r}, "
            f"division={self.division}, key={self.key!r})"
        )


def compute_signature(payload: bytes, secret: str) -> str:
    """Compute the expected signature for a webhook payload.

    Uses HMAC-SHA256 to compute the signature.

    Args:
        payload: Raw webhook payload bytes.
        secret: Webhook secret from Exact Online.

    Returns:
        Hex-encoded signature string.
    """
    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    )
    return signature.hexdigest()


def validate_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Validate webhook signature.

    Compares the provided signature against the computed HMAC-SHA256 signature.
    Uses constant-time comparison to prevent timing attacks.

    Args:
        payload: Raw webhook payload bytes.
        signature: Signature from the X-Exact-Signature header.
        secret: Webhook secret from Exact Online.

    Returns:
        True if the signature is valid, False otherwise.
    """
    expected = compute_signature(payload, secret)
    return hmac.compare_digest(expected.lower(), signature.lower())


def parse_webhook(payload: bytes | str | dict[str, Any]) -> WebhookEvent:
    """Parse a webhook payload into a WebhookEvent.

    Args:
        payload: Webhook payload as bytes, JSON string, or dict.

    Returns:
        Parsed WebhookEvent with extracted fields.

    Raises:
        ValueError: If the payload cannot be parsed or is missing required fields.
    """
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {e}") from e
    else:
        data = payload

    content = data.get("Content", data.get("content", data))

    topic = content.get("Topic", content.get("topic"))
    if not topic:
        raise ValueError("Webhook payload missing 'Topic' field")

    action = content.get("Action", content.get("action"))
    if not action:
        raise ValueError("Webhook payload missing 'Action' field")

    division = content.get("Division", content.get("division"))
    if division is None:
        raise ValueError("Webhook payload missing 'Division' field")

    key = content.get("Key", content.get("key"))
    if not key:
        raise ValueError("Webhook payload missing 'Key' field")

    endpoint = content.get("Endpoint", content.get("endpoint", ""))

    timestamp = None
    ts_str = content.get("Timestamp", content.get("timestamp"))
    if ts_str:
        with contextlib.suppress(ValueError, AttributeError):
            timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

    return WebhookEvent(
        topic=topic,
        action=action,
        division=int(division),
        key=key,
        endpoint=endpoint,
        timestamp=timestamp,
        raw_payload=data,
    )


def validate_and_parse(
    payload: bytes,
    signature: str,
    secret: str,
) -> WebhookEvent:
    """Validate signature and parse webhook payload in one call.

    This is the recommended way to process incoming webhooks. It validates
    the signature first to ensure the webhook is authentic, then parses
    the payload.

    Args:
        payload: Raw webhook payload bytes.
        signature: Signature from the X-Exact-Signature header.
        secret: Webhook secret from Exact Online.

    Returns:
        Parsed and validated WebhookEvent.

    Raises:
        WebhookValidationError: If signature validation fails.
        ValueError: If the payload cannot be parsed.

    Example:
        ```python
        try:
            event = validate_and_parse(
                payload=request_body,
                signature=request.headers["X-Exact-Signature"],
                secret=os.environ["EXACT_WEBHOOK_SECRET"],
            )
            print(f"Got {event.action} for {event.topic}")
        except WebhookValidationError:
            return Response(status_code=401)
        except ValueError as e:
            return Response(status_code=400, body=str(e))
        ```
    """
    if not validate_signature(payload, signature, secret):
        logger.warning("Webhook signature validation failed")
        raise WebhookValidationError("Invalid webhook signature")

    return parse_webhook(payload)
