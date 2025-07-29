import json
import hashlib
import os
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def load_private_key(path: str) -> Ed25519PrivateKey:
    """Load and return an Ed25519 private key from the given path."""
    with open(os.path.expanduser(path), 'rb') as f:
        return Ed25519PrivateKey.from_private_bytes(f.read())


def log_result(result: dict, config: dict):
    """Sign, hash, timestamp, and persist the job result."""
    result['timestamp'] = int(time.time())
    result_json = json.dumps(result, sort_keys=True)
    result['sha256'] = hashlib.sha256(result_json.encode()).hexdigest()
    key = load_private_key(config['private_key_path'])
    result['signature'] = key.sign(result_json.encode()).hex()
    log_path = f"nexapod_{result['job_id']}_log.json"
    with open(log_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Result logged and signed: {log_path}")
