import base64
import hashlib
import hmac
from dataclasses import replace
from typing import Protocol
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from .canonical import canonical_bytes

class Signer(Protocol):
    def sign(self, payload: object) -> str: ...

class Verifier(Protocol):
    def verify(self, payload: object, signature: str) -> bool: ...

class HMACAuthenticator:
    """Deterministic reference authenticator; use HSM/TEE/asymmetric signing in production."""
    def __init__(self, key: bytes):
        self.key = key
    def sign(self, payload: object) -> str:
        return hmac.new(self.key, canonical_bytes(payload), hashlib.sha256).hexdigest()
    def verify(self, payload: object, signature: str) -> bool:
        return hmac.compare_digest(self.sign(payload), signature)

class Ed25519Signer:
    def __init__(self, private_key: Ed25519PrivateKey | None = None):
        self.private_key = private_key or Ed25519PrivateKey.generate()
    def sign(self, payload: object) -> str:
        return base64.b64encode(self.private_key.sign(canonical_bytes(payload))).decode()
    def public_verifier(self) -> "Ed25519Verifier":
        return Ed25519Verifier(self.private_key.public_key())
    def private_bytes(self) -> bytes:
        return self.private_key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )

class Ed25519Verifier:
    def __init__(self, public_key: Ed25519PublicKey):
        self.public_key = public_key
    def verify(self, payload: object, signature: str) -> bool:
        try:
            self.public_key.verify(base64.b64decode(signature), canonical_bytes(payload))
            return True
        except Exception:
            return False


def unsigned(obj):
    return replace(obj, signature="")
