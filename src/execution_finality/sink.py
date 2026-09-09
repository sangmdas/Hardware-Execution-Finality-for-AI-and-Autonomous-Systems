import secrets
from .canonical import sha256_hex
from .crypto import Verifier, unsigned
from .errors import EFCode, FinalityDenied
from .holder import HolderRegistry
from .models import CandidateAct, EffectuationReceipt, FinalityAuthority, HolderProof, RuntimeContext, ValidationEvidence

class FinalitySink:
    """Independent second boundary. No effectuation callback runs before all checks and atomic consumption."""
    def __init__(self, sink_id: str, ped_verifier: Verifier, holder_registry: HolderRegistry, replay_store):
        self.sink_id = sink_id
        self.ped_verifier = ped_verifier
        self.holder_registry = holder_registry
        self.replay_store = replay_store

    def challenge(self) -> str:
        return secrets.token_hex(16)

    def verify_and_effectuate(self, act: CandidateAct, evidence: ValidationEvidence,
                              authority: FinalityAuthority, proof: HolderProof,
                              ctx: RuntimeContext, effect_fn=lambda act: None) -> EffectuationReceipt:
        if authority.sink_id != self.sink_id or act.finality_sink_id != self.sink_id:
            raise FinalityDenied(EFCode.SINK_MISMATCH, "authority/candidate is bound to another sink")
        if not self.ped_verifier.verify(unsigned(evidence), evidence.signature):
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "validation evidence signature invalid")
        if not self.ped_verifier.verify(unsigned(authority), authority.signature):
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "authority signature invalid")
        digest = sha256_hex(act)
        if digest != authority.candidate_digest or evidence.candidate_digest != digest:
            raise FinalityDenied(EFCode.ACT_MISMATCH, "candidate digest does not match authority/evidence")
        if sha256_hex(evidence) != authority.evidence_digest:
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "authority is not bound to supplied evidence")
        if authority.expires_at <= ctx.now or act.expiration_time <= ctx.now:
            raise FinalityDenied(EFCode.STALE_AUTHORITY, "authority or candidate expired")
        if authority.policy_epoch != ctx.policy_epoch:
            raise FinalityDenied(EFCode.POLICY_EPOCH_MISMATCH, "policy changed after issuance")
        if authority.revocation_epoch != ctx.revocation_epoch:
            raise FinalityDenied(EFCode.REVOCATION_STATE_MISMATCH, "revocation state changed after issuance")
        if authority.authority_epoch != ctx.authority_epoch:
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "authority epoch mismatch")
        if authority.protected_state_ref != ctx.protected_state_ref:
            raise FinalityDenied(EFCode.PROTECTED_STATE_MISMATCH, "protected state changed")
        if authority.destination_id != act.destination_id:
            raise FinalityDenied(EFCode.DESTINATION_MISMATCH, "destination substitution")
        if authority.purpose != act.purpose:
            raise FinalityDenied(EFCode.PURPOSE_MISMATCH, "purpose substitution")
        if authority.consequence_class != act.consequence_class:
            raise FinalityDenied(EFCode.CONSEQUENCE_CLASS_MISMATCH, "consequence class substitution")
        if authority.data_precision != act.data_precision:
            raise FinalityDenied(EFCode.PRECISION_MISMATCH, "precision substitution")
        if authority.nonce != act.nonce:
            raise FinalityDenied(EFCode.NONCE_FAILURE, "nonce mismatch")
        if proof.holder_key_id != authority.holder_key_id or proof.authority_id != authority.authority_id:
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "proof-of-possession is not bound to authority")
        if proof.candidate_digest != digest or proof.sink_id != self.sink_id:
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "proof-of-possession act/sink mismatch")
        if not self.holder_registry.verify(proof):
            raise FinalityDenied(EFCode.INVALID_AUTHORITY, "proof-of-possession verification failed")
        # Atomic replay-state transition happens before effectuation. If effect_fn is non-transactional,
        # production deployments need a transactional or idempotent consequence boundary.
        if not self.replay_store.consume_once(authority.authority_id):
            raise FinalityDenied(EFCode.AUTHORITY_ALREADY_USED, "single-use authority already consumed")
        effect_fn(act)
        return EffectuationReceipt(
            authority_id=authority.authority_id, candidate_digest=digest,
            sink_id=self.sink_id, effected_at=ctx.now,
            consequence_class=act.consequence_class, destination_id=act.destination_id)
