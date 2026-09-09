import uuid
from dataclasses import replace
from .canonical import sha256_hex
from .crypto import Signer, unsigned
from .models import CandidateAct, FinalityAuthority, RuntimeContext, ValidationEvidence
from .policy import PolicyProfile

class ProtectedEnforcementDomain:
    """Software reference for the first boundary. It models, but is not itself, a TEE/HSM."""
    def __init__(self, signer: Signer, policy: PolicyProfile, authority_ttl_s: float = 2.0):
        self.signer = signer
        self.policy = policy
        self.authority_ttl_s = authority_ttl_s

    def validate_and_issue(self, act: CandidateAct, ctx: RuntimeContext):
        cold_path = self.policy.evaluate(act, ctx)
        digest = sha256_hex(act)
        evidence = ValidationEvidence(
            evidence_id=str(uuid.uuid4()), candidate_digest=digest,
            policy_epoch=ctx.policy_epoch, revocation_epoch=ctx.revocation_epoch,
            protected_state_ref=ctx.protected_state_ref, sink_id=act.finality_sink_id,
            committed_at=ctx.now, signature="")
        evidence = replace(evidence, signature=self.signer.sign(unsigned(evidence)))
        authority = FinalityAuthority(
            authority_id=str(uuid.uuid4()), candidate_digest=digest,
            evidence_digest=sha256_hex(evidence), sink_id=act.finality_sink_id,
            purpose=act.purpose, scope=act.permitted_scope,
            consequence_class=act.consequence_class,
            destination_id=act.destination_id, jurisdiction=act.jurisdiction,
            data_precision=act.data_precision, nonce=act.nonce,
            policy_epoch=ctx.policy_epoch, authority_epoch=ctx.authority_epoch,
            revocation_epoch=ctx.revocation_epoch,
            protected_state_ref=ctx.protected_state_ref,
            holder_key_id=ctx.holder_key_id,
            issued_at=ctx.now,
            expires_at=min(act.expiration_time, ctx.now + self.authority_ttl_s),
            signature="")
        authority = replace(authority, signature=self.signer.sign(unsigned(authority)))
        return evidence, authority, cold_path
