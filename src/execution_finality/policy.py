from dataclasses import dataclass
from typing import Any
from .errors import EFCode, FinalityDenied
from .models import CandidateAct, ConsequenceClass, RuntimeContext

PRECISION_RANK = {"NONE": 0, "AGGREGATE": 1, "REGION": 2, "CITY": 3, "EXACT": 4}

@dataclass(frozen=True)
class PolicyProfile:
    allowed_tools: frozenset[str]
    allowed_destinations: frozenset[str]
    allowed_consequence_classes: frozenset[ConsequenceClass]
    allowed_purposes: frozenset[str]
    max_precision: str = "EXACT"
    max_amount: float | None = None
    cold_path_amount: float | None = None
    require_attestation: bool = False
    require_provenance: bool = True
    max_delegation_depth: int = 3

    def evaluate(self, act: CandidateAct, ctx: RuntimeContext) -> bool:
        """Return True when the act should use a cold path; otherwise False."""
        if ctx.force_timeout:
            raise FinalityDenied(EFCode.VALIDATION_TIMEOUT, "validation timeout injected")
        if not ctx.policy_available or not ctx.revocation_available:
            raise FinalityDenied(EFCode.AUTHORITY_UNCERTAIN, "policy or revocation state unavailable")
        if act.expiration_time <= ctx.now:
            raise FinalityDenied(EFCode.STALE_AUTHORITY, "candidate expired before authority issuance")
        if act.policy_epoch != ctx.policy_epoch:
            raise FinalityDenied(EFCode.POLICY_EPOCH_MISMATCH, "candidate policy epoch is stale")
        if act.revocation_epoch != ctx.revocation_epoch:
            raise FinalityDenied(EFCode.REVOCATION_STATE_MISMATCH, "candidate revocation epoch is stale")
        if act.protected_state_ref != ctx.protected_state_ref:
            raise FinalityDenied(EFCode.PROTECTED_STATE_MISMATCH, "protected state mismatch")
        if self.require_attestation and not ctx.attestation_ok:
            raise FinalityDenied(EFCode.ATTESTATION_FAILURE, "attestation predicate failed")
        if self.require_provenance and not ctx.provenance_ok:
            raise FinalityDenied(EFCode.INSTRUCTION_PROVENANCE_FAILURE, "instruction provenance failed")
        if self.allowed_tools and act.tool_id not in self.allowed_tools:
            raise FinalityDenied(EFCode.SCOPE_MISMATCH, "tool not inside policy envelope")
        if self.allowed_destinations and act.destination_id not in self.allowed_destinations:
            raise FinalityDenied(EFCode.DESTINATION_MISMATCH, "destination not permitted")
        if act.consequence_class not in self.allowed_consequence_classes:
            raise FinalityDenied(EFCode.CONSEQUENCE_CLASS_MISMATCH, "consequence class not permitted")
        if self.allowed_purposes and act.purpose not in self.allowed_purposes:
            raise FinalityDenied(EFCode.PURPOSE_MISMATCH, "purpose not permitted")
        if PRECISION_RANK.get(act.data_precision, 999) > PRECISION_RANK.get(self.max_precision, -1):
            raise FinalityDenied(EFCode.PRECISION_MISMATCH, "requested precision exceeds policy")
        amount = act.arguments.get("amount")
        if amount is not None and self.max_amount is not None and float(amount) > self.max_amount:
            raise FinalityDenied(EFCode.SCOPE_MISMATCH, "amount exceeds policy maximum")
        depth = int(act.arguments.get("delegation_depth", 0))
        if depth > self.max_delegation_depth:
            raise FinalityDenied(EFCode.SCOPE_MISMATCH, "delegation depth exceeds envelope")
        return bool(amount is not None and self.cold_path_amount is not None and float(amount) >= self.cold_path_amount)
