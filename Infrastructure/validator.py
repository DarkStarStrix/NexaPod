"""
Module for HMAC-based signature generation and log validation.
"""

import hashlib
import hmac

SECRET_KEY = b'supersecret'


def generate_signature(message: bytes) -> str:
    """Generate HMAC-SHA256 signature for a message."""
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()


def validate_log(log: dict) -> bool:
    """Validate the signature of a log entry."""
    expected = generate_signature(str(log.get('id', '')).encode())
    return log.get('signature') == expected
