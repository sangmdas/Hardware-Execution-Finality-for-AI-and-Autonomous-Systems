from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ConsequenceClass(str, Enum):
    TOOL_INVOKE = "TOOL_INVOKE"
    MCP_CALL = "MCP_CALL"
    COMPUTER_USE = "COMPUTER_USE"
    SHELL_EXEC = "SHELL_EXEC"
    MEMORY_WRITE = "MEMORY_WRITE"
    DATA_EXPORT = "DATA_EXPORT"
    PAYMENT = "PAYMENT"
    ACCELERATOR_EGRESS = "ACCELERATOR_EGRESS"
    ACTUATOR = "ACTUATOR"

@dataclass(frozen=True)
class CandidateAct:
    version: str
    candidate_act_id: str
    act_type: str
    initiator_id: str
    application_id: str
    agent_id: str
    model_id: str
    model_or_runtime_state_ref: str
    tool_id: str
    mcp_server_id: str
    function_or_verb: str
    instruction_provenance: str
    purpose: str
    permitted_scope: dict[str, Any]
    consequence_class: ConsequenceClass
    arguments: dict[str, Any]
    resource_or_data_class: str
    destination_id: str
    jurisdiction: str
    data_precision: str
    nonce: str
    creation_time: float
    expiration_time: float
    policy_epoch: int
    authority_epoch: int
    revocation_epoch: int
    protected_state_ref: str
    finality_sink_id: str
    effectuation_boundary_id: str

@dataclass(frozen=True)
class RuntimeContext:
    now: float
    policy_epoch: int
    authority_epoch: int
    revocation_epoch: int
    protected_state_ref: str
    attestation_ok: bool = True
    provenance_ok: bool = True
    policy_available: bool = True
    revocation_available: bool = True
    force_timeout: bool = False
    holder_key_id: str = "holder-1"

@dataclass(frozen=True)
class ValidationEvidence:
    evidence_id: str
    candidate_digest: str
    policy_epoch: int
    revocation_epoch: int
    protected_state_ref: str
    sink_id: str
    committed_at: float
    signature: str

@dataclass(frozen=True)
class FinalityAuthority:
    authority_id: str
    candidate_digest: str
    evidence_digest: str
    sink_id: str
    purpose: str
    scope: dict[str, Any]
    consequence_class: ConsequenceClass
    destination_id: str
    jurisdiction: str
    data_precision: str
    nonce: str
    policy_epoch: int
    authority_epoch: int
    revocation_epoch: int
    protected_state_ref: str
    holder_key_id: str
    issued_at: float
    expires_at: float
    signature: str = field(repr=False)

@dataclass(frozen=True)
class HolderProof:
    holder_key_id: str
    authority_id: str
    candidate_digest: str
    sink_id: str
    challenge: str
    proof: str = field(repr=False)

@dataclass(frozen=True)
class EffectuationReceipt:
    authority_id: str
    candidate_digest: str
    sink_id: str
    effected_at: float
    consequence_class: ConsequenceClass
    destination_id: str
