"""Tests for webhook validation and parsing."""

import json

import pytest

from exact_online.webhooks import (
    WebhookEvent,
    WebhookValidationError,
    compute_signature,
    parse_webhook,
    validate_and_parse,
    validate_signature,
)


class TestComputeSignature:
    """Tests for compute_signature."""

    def test_computes_hmac_sha256(self) -> None:
        """Should compute HMAC-SHA256 signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"

        signature = compute_signature(payload, secret)

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_different_payloads_different_signatures(self) -> None:
        """Different payloads should produce different signatures."""
        secret = "test_secret"

        sig1 = compute_signature(b'{"a": 1}', secret)
        sig2 = compute_signature(b'{"a": 2}', secret)

        assert sig1 != sig2

    def test_different_secrets_different_signatures(self) -> None:
        """Different secrets should produce different signatures."""
        payload = b'{"test": "data"}'

        sig1 = compute_signature(payload, "secret1")
        sig2 = compute_signature(payload, "secret2")

        assert sig1 != sig2


class TestValidateSignature:
    """Tests for validate_signature."""

    def test_valid_signature(self) -> None:
        """Should return True for valid signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        signature = compute_signature(payload, secret)

        assert validate_signature(payload, signature, secret) is True

    def test_invalid_signature(self) -> None:
        """Should return False for invalid signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"

        assert validate_signature(payload, "invalid_signature", secret) is False

    def test_case_insensitive(self) -> None:
        """Should compare signatures case-insensitively."""
        payload = b'{"test": "data"}'
        secret = "test_secret"
        signature = compute_signature(payload, secret)

        assert validate_signature(payload, signature.upper(), secret) is True
        assert validate_signature(payload, signature.lower(), secret) is True


class TestParseWebhook:
    """Tests for parse_webhook."""

    def test_parse_bytes(self) -> None:
        """Should parse bytes payload."""
        payload = json.dumps({
            "Content": {
                "Topic": "PurchaseOrders",
                "Action": "Create",
                "Division": 123,
                "Key": "abc-123",
                "Endpoint": "/api/v1/123/purchaseorder/PurchaseOrders",
            }
        }).encode()

        event = parse_webhook(payload)

        assert event.topic == "PurchaseOrders"
        assert event.action == "Create"
        assert event.division == 123
        assert event.key == "abc-123"

    def test_parse_string(self) -> None:
        """Should parse string payload."""
        payload = json.dumps({
            "Content": {
                "Topic": "Accounts",
                "Action": "Update",
                "Division": 456,
                "Key": "def-456",
            }
        })

        event = parse_webhook(payload)

        assert event.topic == "Accounts"
        assert event.action == "Update"

    def test_parse_dict(self) -> None:
        """Should parse dict payload."""
        payload = {
            "Content": {
                "Topic": "Items",
                "Action": "Delete",
                "Division": 789,
                "Key": "ghi-789",
            }
        }

        event = parse_webhook(payload)

        assert event.topic == "Items"
        assert event.action == "Delete"

    def test_parse_flat_payload(self) -> None:
        """Should parse payload without Content wrapper."""
        payload = {
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
        }

        event = parse_webhook(payload)

        assert event.topic == "PurchaseOrders"

    def test_parse_lowercase_keys(self) -> None:
        """Should handle lowercase keys."""
        payload = {
            "topic": "PurchaseOrders",
            "action": "Create",
            "division": 123,
            "key": "abc-123",
        }

        event = parse_webhook(payload)

        assert event.topic == "PurchaseOrders"

    def test_missing_topic_raises(self) -> None:
        """Should raise ValueError for missing Topic."""
        payload = {
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
        }

        with pytest.raises(ValueError, match="missing 'Topic'"):
            parse_webhook(payload)

    def test_missing_action_raises(self) -> None:
        """Should raise ValueError for missing Action."""
        payload = {
            "Topic": "PurchaseOrders",
            "Division": 123,
            "Key": "abc-123",
        }

        with pytest.raises(ValueError, match="missing 'Action'"):
            parse_webhook(payload)

    def test_missing_division_raises(self) -> None:
        """Should raise ValueError for missing Division."""
        payload = {
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Key": "abc-123",
        }

        with pytest.raises(ValueError, match="missing 'Division'"):
            parse_webhook(payload)

    def test_missing_key_raises(self) -> None:
        """Should raise ValueError for missing Key."""
        payload = {
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
        }

        with pytest.raises(ValueError, match="missing 'Key'"):
            parse_webhook(payload)

    def test_invalid_json_raises(self) -> None:
        """Should raise ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_webhook(b"not json")

    def test_stores_raw_payload(self) -> None:
        """Should store raw payload in event."""
        payload = {
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
            "ExtraField": "extra",
        }

        event = parse_webhook(payload)

        assert event.raw_payload == payload

    def test_parses_timestamp(self) -> None:
        """Should parse ISO timestamp."""
        payload = {
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
            "Timestamp": "2024-01-15T10:30:00Z",
        }

        event = parse_webhook(payload)

        assert event.timestamp is not None
        assert event.timestamp.year == 2024
        assert event.timestamp.month == 1
        assert event.timestamp.day == 15


class TestValidateAndParse:
    """Tests for validate_and_parse."""

    def test_valid_webhook(self) -> None:
        """Should validate and parse valid webhook."""
        payload = json.dumps({
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
        }).encode()
        secret = "test_secret"
        signature = compute_signature(payload, secret)

        event = validate_and_parse(payload, signature, secret)

        assert isinstance(event, WebhookEvent)
        assert event.topic == "PurchaseOrders"

    def test_invalid_signature_raises(self) -> None:
        """Should raise WebhookValidationError for invalid signature."""
        payload = json.dumps({
            "Topic": "PurchaseOrders",
            "Action": "Create",
            "Division": 123,
            "Key": "abc-123",
        }).encode()

        with pytest.raises(WebhookValidationError, match="Invalid webhook signature"):
            validate_and_parse(payload, "wrong_signature", "test_secret")

    def test_invalid_payload_raises(self) -> None:
        """Should raise ValueError for invalid payload after signature validation."""
        payload = json.dumps({"Topic": "PurchaseOrders"}).encode()
        secret = "test_secret"
        signature = compute_signature(payload, secret)

        with pytest.raises(ValueError, match="missing"):
            validate_and_parse(payload, signature, secret)


class TestWebhookEvent:
    """Tests for WebhookEvent dataclass."""

    def test_repr(self) -> None:
        """Should have readable repr."""
        event = WebhookEvent(
            topic="PurchaseOrders",
            action="Create",
            division=123,
            key="abc-123",
            endpoint="/api/v1/123/purchaseorder/PurchaseOrders",
        )

        repr_str = repr(event)

        assert "PurchaseOrders" in repr_str
        assert "Create" in repr_str
        assert "123" in repr_str
        assert "abc-123" in repr_str
