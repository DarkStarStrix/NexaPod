import hashlib
import hmac

SECRET_KEY = b'supersecret'

def generate_signature(message: bytes) -> str:
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()

def validate_log(log: dict) -> bool:
    # Validate the signature and hash of the log.
    expected_signature = generate_signature(str(log.get('id', '')).encode())
    return log.get('signature') == expected_signature
