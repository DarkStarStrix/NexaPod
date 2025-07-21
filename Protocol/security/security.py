from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization, hashes

def generate_node_keypair():
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    # ...serialize & store in DB...
    return sk, pk

def sign_log(sk, message: bytes) -> bytes:
    return sk.sign(message)

