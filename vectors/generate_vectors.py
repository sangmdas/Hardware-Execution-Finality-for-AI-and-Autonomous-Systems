import json
from execution_finality import CandidateAct, ConsequenceClass, HMACAuthenticator
from execution_finality.canonical import sha256_hex, canonical_bytes

act=CandidateAct(
    version="1",candidate_act_id="act-0001",act_type="MCP_CALL",initiator_id="user-1",
    application_id="agent-host-1",agent_id="enterprise-agent-27",model_id="model-build-X",
    model_or_runtime_state_ref="runtime-good",tool_id="customer-payment-api",mcp_server_id="payments-mcp-3",
    function_or_verb="issue_refund",instruction_provenance="authenticated-support-workflow",purpose="customer-refund",
    permitted_scope={"currency":"USD","max_amount":500},consequence_class=ConsequenceClass.MCP_CALL,
    arguments={"amount":50,"currency":"USD","customer_id":"18422"},resource_or_data_class="financial",
    destination_id="payments-prod",jurisdiction="US",data_precision="EXACT",nonce="nonce-0001",
    creation_time=1700000000.0,expiration_time=1700000010.0,policy_epoch=481,authority_epoch=9,
    revocation_epoch=12,protected_state_ref="state-481-12",finality_sink_id="mcp-dispatcher",
    effectuation_boundary_id="dispatch-boundary-1")
auth=HMACAuthenticator(b"deterministic-reference-vector-key")
out={
  "description":"Deterministic canonicalization vector. The HMAC key is public test material and MUST NOT be used in deployment.",
  "candidate":json.loads(canonical_bytes(act)),
  "candidate_sha256":sha256_hex(act),
  "candidate_hmac_sha256":auth.sign(act)
}
print(json.dumps(out,indent=2,sort_keys=True))
