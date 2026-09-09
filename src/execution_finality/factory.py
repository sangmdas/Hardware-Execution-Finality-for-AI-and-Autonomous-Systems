import time, uuid
from .models import CandidateAct, ConsequenceClass, RuntimeContext


def make_candidate(**overrides):
    now = overrides.pop("now", time.time())
    base = dict(
        version="1", candidate_act_id=str(uuid.uuid4()), act_type="MCP_CALL",
        initiator_id="user-1", application_id="agent-host-1", agent_id="enterprise-agent-27",
        model_id="model-build-X", model_or_runtime_state_ref="runtime-good",
        tool_id="customer-payment-api", mcp_server_id="payments-mcp-3", function_or_verb="issue_refund",
        instruction_provenance="authenticated-support-workflow", purpose="customer-refund",
        permitted_scope={"currency":"USD","max_amount":500}, consequence_class=ConsequenceClass.MCP_CALL,
        arguments={"amount":50,"currency":"USD","customer_id":"18422"},
        resource_or_data_class="financial", destination_id="payments-prod", jurisdiction="US",
        data_precision="EXACT", nonce=uuid.uuid4().hex, creation_time=now,
        expiration_time=now+10, policy_epoch=481, authority_epoch=9, revocation_epoch=12,
        protected_state_ref="state-481-12", finality_sink_id="mcp-dispatcher",
        effectuation_boundary_id="dispatch-boundary-1")
    base.update(overrides)
    return CandidateAct(**base)


def make_context(act, now=None, **overrides):
    base = dict(now=act.creation_time + 0.001 if now is None else now,
                policy_epoch=act.policy_epoch, authority_epoch=act.authority_epoch,
                revocation_epoch=act.revocation_epoch, protected_state_ref=act.protected_state_ref,
                holder_key_id="holder-1")
    base.update(overrides)
    return RuntimeContext(**base)
