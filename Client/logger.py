import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import os

def load_private_key(path):
    with open(os.path.expanduser(path), 'rb') as f:
        return Ed25519PrivateKey.from_private_bytes(f.read())

def log_result(result, config):
    # Add timestamp and hash
    result['timestamp'] = int(time.time())
    result_json = json.dumps(result, sort_keys=True)
    result['sha256'] = hashlib.sha256(result_json.encode()).hexdigest()
    # Sign result
    key = load_private_key(config['private_key_path'])
    signature = key.sign(result_json.encode())
    result['signature'] = signature.hex()
    # Write log
    log_path = f"nexapod_{result['job_id']}_log.json"
    with open(log_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Result logged and signed: {log_path}")

