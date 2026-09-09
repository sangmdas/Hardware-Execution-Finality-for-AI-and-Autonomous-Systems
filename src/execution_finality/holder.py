import hashlib
import hmac
from .canonical import canonical_bytes
from .models import FinalityAuthority, HolderProof

class ProtectedHolder:
    """Reference proof-of-possession holder. Key is intentionally not serialized with authority."""
    def __init__(self, key_id: str, key: bytes):
        self.key_id = key_id
        self.key = key
    def prove(self, authority: FinalityAuthority, challenge: str) -> HolderProof:
        payload = {
            "holder_key_id": self.key_id,
            "authority_id": authority.authority_id,
            "candidate_digest": authority.candidate_digest,
            "sink_id": authority.sink_id,
            "challenge": challenge,
        }
        proof = hmac.new(self.key, canonical_bytes(payload), hashlib.sha256).hexdigest()
        return HolderProof(proof=proof, **payload)

class HolderRegistry:
    def __init__(self, keys: dict[str, bytes]):
        self.keys = dict(keys)
    def verify(self, proof: HolderProof) -> bool:
        key = self.keys.get(proof.holder_key_id)
        if key is None:
            return False
        payload = {
            "holder_key_id": proof.holder_key_id,
            "authority_id": proof.authority_id,
            "candidate_digest": proof.candidate_digest,
            "sink_id": proof.sink_id,
            "challenge": proof.challenge,
        }
        expected = hmac.new(key, canonical_bytes(payload), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, proof.proof)
